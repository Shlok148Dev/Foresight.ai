"""
Foresight — Signal Ingestion & Retrieval API
==============================================
Week 2: Added Redis caching, batch ingestion, real NLP pipeline processing.
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
from app.cache.redis_cache import (
    cache_get, cache_set, cache_delete_pattern,
    signal_list_key, signal_detail_key,
)

logger = logging.getLogger("foresight.signals")
router = APIRouter(prefix="/signals", tags=["signals"])


# ── Schemas ──────────────────────────────────────────────────────

class SignalCreate(BaseModel):
    text: str = Field(min_length=10, max_length=2000)
    platform: PlatformType
    author: Optional[str] = None
    author_followers: Optional[int] = None
    url: Optional[str] = None
    language: str = "en"
    engagement: dict = {}
    metadata: dict = {}


class SignalOut(BaseModel):
    id: str
    text: str
    platform: str
    author: Optional[str]
    url: Optional[str]
    language: str
    created_at: str

    class Config:
        from_attributes = True


class SignalListResponse(BaseModel):
    signals: list[SignalOut]
    total: int
    limit: int
    offset: int


class BatchSignalCreate(BaseModel):
    """Batch signal ingestion — up to 100 signals at once."""
    signals: list[SignalCreate] = Field(max_length=100)


class BatchSignalResponse(BaseModel):
    ingested: int
    failed: int
    signal_ids: list[str]


# ── Helpers ──────────────────────────────────────────────────────

def _signal_to_out(s: Signal) -> SignalOut:
    return SignalOut(
        id=str(s.id),
        text=s.text,
        platform=s.platform.value,
        author=s.author,
        url=s.url,
        language=s.language or "en",
        created_at=s.created_at.isoformat(),
    )


# ── Endpoints ────────────────────────────────────────────────────

@router.post("/ingest", response_model=SignalOut, status_code=201)
async def ingest_signal(
    data: SignalCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Ingest a single raw signal from an external platform."""
    signal = Signal(
        text=data.text,
        platform=data.platform,
        author=data.author,
        author_followers=data.author_followers,
        url=data.url,
        language=data.language,
        engagement=data.engagement,
        metadata_=data.metadata,
    )
    db.add(signal)
    await db.flush()

    logger.info(f"Signal ingested: {signal.id} [{data.platform.value}]")

    # Invalidate signal list cache
    await cache_delete_pattern("signals:list*")

    # Queue for real-time NLP matching
    background_tasks.add_task(_process_signal_async, str(signal.id))

    return _signal_to_out(signal)


@router.post("/ingest/batch", response_model=BatchSignalResponse, status_code=201)
async def batch_ingest_signals(
    data: BatchSignalCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Batch ingest up to 100 signals at once.
    Optimized for high-throughput ingestion from scrapers/collectors.
    """
    ingested = 0
    failed = 0
    signal_ids = []

    for item in data.signals:
        try:
            signal = Signal(
                text=item.text,
                platform=item.platform,
                author=item.author,
                author_followers=item.author_followers,
                url=item.url,
                language=item.language,
                engagement=item.engagement,
                metadata_=item.metadata,
            )
            db.add(signal)
            await db.flush()
            signal_ids.append(str(signal.id))
            ingested += 1
        except Exception as e:
            logger.warning(f"Failed to ingest signal: {e}")
            failed += 1

    logger.info(f"Batch ingestion: {ingested} ingested, {failed} failed")

    # Invalidate caches
    await cache_delete_pattern("signals:list*")

    # Queue batch for NLP processing
    background_tasks.add_task(_process_batch_signals, signal_ids)

    return BatchSignalResponse(
        ingested=ingested,
        failed=failed,
        signal_ids=signal_ids,
    )


@router.get("/", response_model=SignalListResponse)
async def list_signals(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    platform: Optional[PlatformType] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List signals with optional platform filter, pagination, and Redis caching."""
    # Check cache
    cache_key = signal_list_key(
        platform=platform.value if platform else None,
        limit=limit, offset=offset,
    )
    cached = await cache_get(cache_key)
    if cached:
        return SignalListResponse(**cached)

    # Build query
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

    response = SignalListResponse(
        signals=[_signal_to_out(s) for s in signals],
        total=total, limit=limit, offset=offset,
    )

    # Cache for 5 minutes
    await cache_set(cache_key, response.model_dump(), ttl=300)
    return response


@router.get("/{signal_id}", response_model=SignalOut)
async def get_signal(
    signal_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get a single signal by ID."""
    from uuid import UUID

    # Check cache
    cache_key = signal_detail_key(signal_id)
    cached = await cache_get(cache_key)
    if cached:
        return SignalOut(**cached)

    try:
        uid = UUID(signal_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid signal ID format")

    result = await db.execute(select(Signal).where(Signal.id == uid))
    signal = result.scalar_one_or_none()
    if not signal:
        raise HTTPException(status_code=404, detail="Signal not found")

    out = _signal_to_out(signal)
    await cache_set(cache_key, out.model_dump(), ttl=600)  # Cache 10 min
    return out


# ── Background Tasks ─────────────────────────────────────────────

async def _process_signal_async(signal_id: str):
    """Background: process single signal through NLP pipeline."""
    try:
        from app.db.database import async_session_factory
        from app.services.detection import process_single_signal

        async with async_session_factory() as session:
            result = await process_single_signal(signal_id, session)
            await session.commit()
            if result:
                logger.info(f"Signal {signal_id} matched to detection '{result.topic}'")
                await cache_delete_pattern("detections:*")
    except Exception as e:
        logger.error(f"Error processing signal {signal_id}: {e}")


async def _process_batch_signals(signal_ids: list[str]):
    """Background: process batch of signals (triggers full pipeline if enough signals)."""
    try:
        from app.db.database import async_session_factory
        from app.services.detection import process_single_signal, run_detection_pipeline

        async with async_session_factory() as session:
            # Process each signal individually first
            for sid in signal_ids:
                await process_single_signal(sid, session)

            # If batch is large enough, run full pipeline
            if len(signal_ids) >= 5:
                logger.info(f"Batch large enough ({len(signal_ids)}), running full detection pipeline")
                await run_detection_pipeline(session, window_hours=24)

            await session.commit()
            await cache_delete_pattern("detections:*")
    except Exception as e:
        logger.error(f"Error processing batch signals: {e}")
