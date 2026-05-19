"""
Foresight — Signal Ingestion & Retrieval API
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
import logging

from app.db.database import get_db
from app.models.database import Signal, PlatformType, User
from app.services.auth import get_current_user

logger = logging.getLogger("foresight.signals")
router = APIRouter(prefix="/signals", tags=["signals"])


class SignalCreate(BaseModel):
    text: str = Field(min_length=10, max_length=2000)
    platform: PlatformType
    author: Optional[str] = None
    url: Optional[str] = None
    metadata: dict = {}


class SignalOut(BaseModel):
    id: str
    text: str
    platform: str
    author: Optional[str]
    url: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


class SignalListResponse(BaseModel):
    signals: list[SignalOut]
    total: int
    limit: int
    offset: int


@router.post("/ingest", response_model=SignalOut, status_code=201)
async def ingest_signal(
    data: SignalCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Ingest a raw signal from an external platform."""
    signal = Signal(
        text=data.text,
        platform=data.platform,
        author=data.author,
        url=data.url,
        metadata_=data.metadata,
    )
    db.add(signal)
    await db.flush()

    logger.info(f"Signal ingested: {signal.id} [{data.platform.value}]")
    background_tasks.add_task(_process_signal, str(signal.id))

    return SignalOut(
        id=str(signal.id), text=signal.text, platform=signal.platform.value,
        author=signal.author, url=signal.url,
        created_at=signal.created_at.isoformat(),
    )


@router.get("/", response_model=SignalListResponse)
async def list_signals(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    platform: Optional[PlatformType] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List signals with optional platform filter and pagination."""
    query = select(Signal)
    count_query = select(func.count(Signal.id))

    if platform:
        query = query.where(Signal.platform == platform)
        count_query = count_query.where(Signal.platform == platform)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    result = await db.execute(
        query.order_by(Signal.created_at.desc()).limit(limit).offset(offset)
    )
    signals = result.scalars().all()

    return SignalListResponse(
        signals=[
            SignalOut(
                id=str(s.id), text=s.text, platform=s.platform.value,
                author=s.author, url=s.url, created_at=s.created_at.isoformat(),
            )
            for s in signals
        ],
        total=total, limit=limit, offset=offset,
    )


@router.get("/{signal_id}", response_model=SignalOut)
async def get_signal(
    signal_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get a single signal by ID."""
    from uuid import UUID
    try:
        uid = UUID(signal_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid signal ID format")

    result = await db.execute(select(Signal).where(Signal.id == uid))
    signal = result.scalar_one_or_none()
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")

    return SignalOut(
        id=str(signal.id), text=signal.text, platform=signal.platform.value,
        author=signal.author, url=signal.url,
        created_at=signal.created_at.isoformat(),
    )


async def _process_signal(signal_id: str):
    """Background: queue signal for NLP detection pipeline."""
    logger.info(f"Processing signal {signal_id} (stub — NLP pipeline Week 2)")
