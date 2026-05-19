"""
Foresight — Detections API
============================
CRUD endpoints for trend detections + pipeline trigger.
Follows Technical Bible §4.2 — Detection Endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
import logging

from app.db.database import get_db
from app.models.database import Detection, SpreadStage, User
from app.services.auth import get_current_user
from app.cache.redis_cache import (
    cache_get, cache_set, cache_delete_pattern,
    detection_list_key, detection_detail_key,
)

logger = logging.getLogger("foresight.api.detections")
router = APIRouter(prefix="/detections", tags=["detections"])


# ── Schemas ──────────────────────────────────────────────────────

class DetectionOut(BaseModel):
    id: str
    topic: str
    description: Optional[str]
    stage: str
    confidence: float
    signal_count: int
    velocity: float
    platforms: list[str]
    keywords: list[str]
    action_prompt: Optional[str]
    first_seen: str
    last_updated: str

    class Config:
        from_attributes = True


class DetectionListResponse(BaseModel):
    detections: list[DetectionOut]
    total: int
    limit: int
    offset: int


class PipelineResponse(BaseModel):
    status: str
    detections_created: int
    signals_processed: int
    message: str


# ── Helper ───────────────────────────────────────────────────────

def _detection_to_out(d: Detection) -> DetectionOut:
    return DetectionOut(
        id=str(d.id),
        topic=d.topic,
        description=d.description,
        stage=d.stage.value if d.stage else "embryonic",
        confidence=d.confidence or 0.0,
        signal_count=d.signal_count or 0,
        velocity=d.velocity or 0.0,
        platforms=d.platforms or [],
        keywords=d.keywords or [],
        action_prompt=d.action_prompt,
        first_seen=d.first_seen.isoformat() if d.first_seen else "",
        last_updated=d.last_updated.isoformat() if d.last_updated else "",
    )


# ── Endpoints ────────────────────────────────────────────────────

@router.get("/", response_model=DetectionListResponse)
async def list_detections(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    stage: Optional[SpreadStage] = None,
    min_confidence: Optional[float] = Query(default=None, ge=0.0, le=1.0),
    sort_by: str = Query(default="confidence", pattern="^(confidence|velocity|signal_count|first_seen)$"),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    List trend detections with filtering and sorting.

    Filters:
        - stage: embryonic, emerging, accelerating, peaking, declining
        - min_confidence: minimum confidence score (0.0 – 1.0)
        - sort_by: confidence | velocity | signal_count | first_seen
    """
    # Check cache first
    cache_key = detection_list_key(
        stage=stage.value if stage else None, limit=limit, offset=offset
    )
    cached = await cache_get(cache_key)
    if cached:
        return DetectionListResponse(**cached)

    # Build query
    query = select(Detection)
    count_query = select(func.count(Detection.id))

    if stage:
        query = query.where(Detection.stage == stage)
        count_query = count_query.where(Detection.stage == stage)

    if min_confidence is not None:
        query = query.where(Detection.confidence >= min_confidence)
        count_query = count_query.where(Detection.confidence >= min_confidence)

    # Sorting
    sort_column = {
        "confidence": Detection.confidence.desc(),
        "velocity": Detection.velocity.desc(),
        "signal_count": Detection.signal_count.desc(),
        "first_seen": Detection.first_seen.desc(),
    }.get(sort_by, Detection.confidence.desc())

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    result = await db.execute(
        query.order_by(sort_column).limit(limit).offset(offset)
    )
    detections = result.scalars().all()

    response = DetectionListResponse(
        detections=[_detection_to_out(d) for d in detections],
        total=total,
        limit=limit,
        offset=offset,
    )

    # Cache the result
    await cache_set(cache_key, response.model_dump(), ttl=120)  # 2 min cache for detections
    return response


@router.get("/{detection_id}", response_model=DetectionOut)
async def get_detection(
    detection_id: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get a single detection by ID with full details."""
    from uuid import UUID

    # Check cache
    cache_key = detection_detail_key(detection_id)
    cached = await cache_get(cache_key)
    if cached:
        return DetectionOut(**cached)

    try:
        uid = UUID(detection_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid detection ID format")

    result = await db.execute(select(Detection).where(Detection.id == uid))
    detection = result.scalar_one_or_none()

    if not detection:
        raise HTTPException(status_code=404, detail="Detection not found")

    out = _detection_to_out(detection)
    await cache_set(cache_key, out.model_dump(), ttl=120)
    return out


@router.post("/run-pipeline", response_model=PipelineResponse)
async def trigger_pipeline(
    window_hours: int = Query(default=24, ge=1, le=168),
    background_tasks: BackgroundTasks = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Manually trigger the NLP detection pipeline.
    Clusters recent signals and creates new detections.
    """
    from app.services.detection import run_detection_pipeline

    detections = await run_detection_pipeline(db, window_hours=window_hours)

    # Invalidate detection caches
    await cache_delete_pattern("detections:*")

    return PipelineResponse(
        status="completed",
        detections_created=len(detections),
        signals_processed=sum(d.signal_count or 0 for d in detections),
        message=f"Pipeline found {len(detections)} trend clusters in the last {window_hours}h",
    )


@router.get("/stages/summary")
async def stage_summary(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get a summary count of detections by spread stage."""
    result = await db.execute(
        select(Detection.stage, func.count(Detection.id))
        .group_by(Detection.stage)
    )

    summary = {row[0].value: row[1] for row in result.all()}

    # Ensure all stages are present
    for stage in SpreadStage:
        if stage.value not in summary:
            summary[stage.value] = 0

    return {
        "stages": summary,
        "total": sum(summary.values()),
    }
