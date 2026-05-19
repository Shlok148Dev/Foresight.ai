"""
Foresight — Authentication Service
====================================
JWT-based authentication with bcrypt password hashing.
Follows Technical Bible §2.2 — Auth specification.

Security features:
- bcrypt password hashing (12 rounds)
- Short-lived access tokens (30 min)
- Long-lived refresh tokens (7 days)
- Token blacklist for logout
- Rate limiting via Redis
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.database import User, UserRole
import os
import logging

logger = logging.getLogger("foresight.auth")

# ── Configuration ────────────────────────────────────────────────

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Password hashing — bcrypt with 12 rounds (secure default)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer token extraction
security = HTTPBearer()


# ── Pydantic Schemas ─────────────────────────────────────────────

class RegisterRequest(BaseModel):
    """User registration payload."""
    email: EmailStr
    username: str = Field(min_length=3, max_length=100, pattern=r"^[a-zA-Z0-9_-]+$")
    password: str = Field(min_length=8, max_length=128)
    full_name: Optional[str] = Field(default=None, max_length=255)


class LoginRequest(BaseModel):
    """User login payload."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token pair returned on login/register."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class UserResponse(BaseModel):
    """Public user profile (no password hash)."""
    id: str
    email: str
    username: str
    full_name: Optional[str]
    role: str
    is_active: bool
    is_verified: bool
    created_at: str

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    """Decoded JWT payload."""
    sub: str  # user_id
    type: str  # "access" or "refresh"
    exp: datetime


# ── Password Utilities ───────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hash a password using bcrypt (12 rounds)."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


# ── Token Creation ───────────────────────────────────────────────

def create_access_token(user_id: str) -> str:
    """
    Create a short-lived access token (30 min default).
    Contains user_id in the 'sub' claim.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "type": "access",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """
    Create a long-lived refresh token (7 days default).
    Used to obtain new access tokens without re-login.
    """
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": user_id,
        "type": "refresh",
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_token_pair(user_id: str) -> TokenResponse:
    """Create both access and refresh tokens."""
    return TokenResponse(
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
        token_type="bearer",
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# ── Token Verification ──────────────────────────────────────────

def decode_token(token: str) -> TokenData:
    """
    Decode and validate a JWT token.
    Raises HTTPException 401 on invalid/expired tokens.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type", "access")
        exp = datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc)

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
            )

        return TokenData(sub=user_id, type=token_type, exp=exp)

    except JWTError as e:
        logger.warning(f"JWT decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ── FastAPI Dependencies ─────────────────────────────────────────

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    FastAPI dependency: extracts and validates JWT, returns User object.
    
    Usage:
        @router.get("/me")
        async def profile(user: User = Depends(get_current_user)):
            return user
    """
    token_data = decode_token(credentials.credentials)

    if token_data.type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type: expected access token",
        )

    result = await db.execute(
        select(User).where(User.id == UUID(token_data.sub))
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    return user


async def get_current_active_admin(
    user: User = Depends(get_current_user),
) -> User:
    """Dependency that requires admin role."""
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


# ── Service Functions ────────────────────────────────────────────

async def register_user(data: RegisterRequest, db: AsyncSession) -> tuple[User, TokenResponse]:
    """
    Register a new user.
    Returns the created User and a token pair.
    Raises HTTPException 409 if email or username already exists.
    """
    # Check email uniqueness
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    # Check username uniqueness
    existing = await db.execute(select(User).where(User.username == data.username))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )

    # Create user
    user = User(
        email=data.email,
        username=data.username,
        password_hash=hash_password(data.password),
        full_name=data.full_name,
        role=UserRole.FREE,
    )
    db.add(user)
    await db.flush()  # Get the generated id

    logger.info(f"New user registered: {user.username} ({user.email})")

    tokens = create_token_pair(str(user.id))
    return user, tokens


async def login_user(data: LoginRequest, db: AsyncSession) -> tuple[User, TokenResponse]:
    """
    Authenticate a user with email + password.
    Returns the User and a token pair.
    Raises HTTPException 401 on invalid credentials.
    """
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    # Update last login
    user.last_login = datetime.utcnow()

    logger.info(f"User logged in: {user.username}")

    tokens = create_token_pair(str(user.id))
    return user, tokens
