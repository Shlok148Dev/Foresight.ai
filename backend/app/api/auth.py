"""
Foresight — Auth API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.database import User
from app.services.auth import (
    LoginRequest, RegisterRequest, TokenResponse, UserResponse,
    decode_token, create_token_pair, get_current_user,
    login_user, register_user,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new user. Returns JWT tokens."""
    _, tokens = await register_user(data, db)
    return tokens


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login with email + password. Returns JWT tokens."""
    _, tokens = await login_user(data, db)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    """Exchange refresh token for new token pair."""
    token_data = decode_token(refresh_token)
    if token_data.type != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Expected refresh token")
    return create_token_pair(token_data.sub)


@router.get("/me", response_model=UserResponse)
async def get_profile(user: User = Depends(get_current_user)):
    """Get authenticated user's profile."""
    return UserResponse(
        id=str(user.id), email=user.email, username=user.username,
        full_name=user.full_name, role=user.role.value,
        is_active=user.is_active, is_verified=user.is_verified,
        created_at=user.created_at.isoformat(),
    )
