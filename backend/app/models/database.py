"""
Foresight — Database Models (SQLAlchemy ORM)
=============================================
Complete schema for: Users, Signals, Detections, Forecasts, Simulations.
Follows the Technical Bible §2.1 specification exactly.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
    Text,
    ForeignKey,
    Index,
    Enum as SAEnum,
    JSON,
    Uuid,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.db.database import Base


# ── Enums ────────────────────────────────────────────────────────

class SpreadStage(str, enum.Enum):
    """Signal spread lifecycle stages."""
    EMBRYONIC = "embryonic"
    EMERGING = "emerging"
    ACCELERATING = "accelerating"
    PEAKING = "peaking"
    DECLINING = "declining"


class UserRole(str, enum.Enum):
    """User access tiers."""
    FREE = "free"
    PRO = "pro"
    TEAM = "team"
    ENTERPRISE = "enterprise"
    ADMIN = "admin"


class PlatformType(str, enum.Enum):
    """Supported signal source platforms."""
    TWITTER = "twitter"
    REDDIT = "reddit"
    DISCORD = "discord"
    TIKTOK = "tiktok"
    TELEGRAM = "telegram"
    GITHUB = "github"
    YOUTUBE = "youtube"
    HACKERNEWS = "hackernews"
    SUBSTACK = "substack"
    OTHER = "other"


# ── User Model ───────────────────────────────────────────────────

class User(Base):
    """
    User account.
    Supports JWT auth with bcrypt password hashing.
    """
    __tablename__ = "users"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    role = Column(SAEnum(UserRole), default=UserRole.FREE, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # Preferences
    domains = Column(JSON, default=list)  # User's tracked domains
    preferences = Column(JSON, default=dict)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    last_login = Column(DateTime, nullable=True)

    # Relationships
    saved_signals = relationship("SavedSignal", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_users_email", "email"),
        Index("idx_users_username", "username"),
        Index("idx_users_role", "role"),
        Index("idx_users_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<User {self.username} ({self.email})>"


# ── Signal Model ─────────────────────────────────────────────────

class Signal(Base):
    """
    Raw signal ingested from external platforms.
    Represents a single data point (tweet, post, comment, etc.).
    """
    __tablename__ = "signals"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    text = Column(Text, nullable=False)
    platform = Column(SAEnum(PlatformType), nullable=False)
    author = Column(String(255), nullable=True)
    author_followers = Column(Integer, nullable=True)
    url = Column(String(500), nullable=True)
    language = Column(String(10), default="en")
    engagement = Column(JSON, default=dict)  # {likes, shares, comments, views}
    metadata_ = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ingested_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Foreign keys
    detection_id = Column(
        Uuid(as_uuid=True), ForeignKey("detections.id"), nullable=True
    )

    # Relationships
    detection = relationship("Detection", back_populates="signals")

    __table_args__ = (
        Index("idx_signals_platform_created", "platform", "created_at"),
        Index("idx_signals_created_at", "created_at"),
        Index("idx_signals_detection_id", "detection_id"),
    )

    def __repr__(self) -> str:
        return f"<Signal {self.id} [{self.platform.value}]>"


# ── Detection Model ──────────────────────────────────────────────

class Detection(Base):
    """
    Detected trend — a cluster of related signals
    identified by the NLP pipeline.
    """
    __tablename__ = "detections"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    stage = Column(SAEnum(SpreadStage), default=SpreadStage.EMBRYONIC, nullable=False)
    confidence = Column(Float, nullable=False, default=0.0)  # 0.0 – 1.0
    signal_count = Column(Integer, default=0)
    velocity = Column(Float, default=0.0)  # signals per hour
    platforms = Column(JSON, default=list)
    communities = Column(JSON, default=list)
    keywords = Column(JSON, default=list)
    action_prompt = Column(Text, nullable=True)  # "The one thing to do right now"
    metadata_ = Column("metadata", JSON, default=dict)

    # Timestamps
    first_seen = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_updated = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    signals = relationship("Signal", back_populates="detection")
    forecasts = relationship("Forecast", back_populates="detection", cascade="all, delete-orphan")
    simulations = relationship(
        "Simulation", back_populates="detection", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_detections_topic", "topic"),
        Index("idx_detections_stage", "stage"),
        Index("idx_detections_confidence", "confidence"),
        Index("idx_detections_first_seen", "first_seen"),
        Index("idx_detections_velocity", "velocity"),
    )

    def __repr__(self) -> str:
        return f"<Detection '{self.topic}' [{self.stage.value}] conf={self.confidence:.2f}>"


# ── Forecast Model ───────────────────────────────────────────────

class Forecast(Base):
    """
    Time-series prediction for a detection.
    Generated by Prophet / pytorch-forecasting.
    """
    __tablename__ = "forecasts"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    detection_id = Column(
        Uuid(as_uuid=True), ForeignKey("detections.id"), nullable=False
    )
    forecast_date = Column(DateTime, nullable=False)
    predicted_mentions = Column(Integer, nullable=True)
    predicted_stage = Column(SAEnum(SpreadStage), nullable=True)
    predicted_velocity = Column(Float, nullable=True)
    confidence_lower = Column(Float, nullable=True)
    confidence_upper = Column(Float, nullable=True)
    model_version = Column(String(50), default="prophet-v1")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    detection = relationship("Detection", back_populates="forecasts")

    __table_args__ = (
        Index("idx_forecasts_detection_id", "detection_id"),
        Index("idx_forecasts_forecast_date", "forecast_date"),
    )

    def __repr__(self) -> str:
        return f"<Forecast {self.detection_id} → {self.forecast_date}>"


# ── Simulation Model ────────────────────────────────────────────

class Simulation(Base):
    """
    MiroFish multi-agent simulation result.
    Stores spread path, virality coefficient, and decay probability.
    """
    __tablename__ = "simulations"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    detection_id = Column(
        Uuid(as_uuid=True), ForeignKey("detections.id"), nullable=False
    )
    agent_count = Column(Integer, default=1000)
    monte_carlo_runs = Column(Integer, default=50)
    simulation_data = Column(JSON, default=dict)
    spread_path = Column(JSON, default=dict)
    virality_coefficient = Column(Float, nullable=True)
    decay_probability = Column(Float, nullable=True)
    mainstream_eta_hours = Column(Float, nullable=True)
    accuracy_score = Column(Float, nullable=True)  # post-hoc validation
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    detection = relationship("Detection", back_populates="simulations")

    __table_args__ = (
        Index("idx_simulations_detection_id", "detection_id"),
        Index("idx_simulations_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Simulation {self.detection_id} agents={self.agent_count}>"


# ── SavedSignal (User ↔ Detection junction) ─────────────────────

class SavedSignal(Base):
    """User's saved/watchlisted detections."""
    __tablename__ = "saved_signals"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False)
    detection_id = Column(
        Uuid(as_uuid=True), ForeignKey("detections.id"), nullable=False
    )
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="saved_signals")
    detection = relationship("Detection")

    __table_args__ = (
        Index("idx_saved_user_id", "user_id"),
        Index("idx_saved_detection_id", "detection_id"),
    )
