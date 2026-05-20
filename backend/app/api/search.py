"""
Foresight — Search API Router
==============================
Provides endpoints for text-based and keyword-based search
across both raw Signals and detected Trend Clusters.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.db.database import get_db
from app.models.database import Signal, Detection, User
from app.services.auth import get_current_user
from app.api.signals import _signal_to_out, SignalOut
from app.api.detections import _detection_to_out, DetectionOut

router = APIRouter(prefix="/search", tags=["search"])


class SearchResponse(BaseModel):
    signals: list[SignalOut]
    detections: list[DetectionOut]
    query: str


@router.get("/", response_model=SearchResponse)
async def search_all(
    q: str = Query(default="", min_length=1),
    limit: int = Query(default=20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Search both signals and detections matching the query string.
    Case-insensitive search against text, topics, and keywords.
    """
    search_pattern = f"%{q}%"

    # Search signals
    signal_query = (
        select(Signal)
        .where(Signal.text.ilike(search_pattern))
        .order_by(Signal.created_at.desc())
        .limit(limit)
    )
    signal_results = await db.execute(signal_query)
    signals = signal_results.scalars().all()

    # Search detections
    detection_query = (
        select(Detection)
        .where(
            or_(
                Detection.topic.ilike(search_pattern),
                Detection.description.ilike(search_pattern),
                Detection.keywords.any(q) # Matches array elements
            )
        )
        .order_by(Detection.confidence.desc())
        .limit(limit)
    )
    detection_results = await db.execute(detection_query)
    detections = detection_results.scalars().all()

    return SearchResponse(
        signals=[_signal_to_out(s) for s in signals],
        detections=[_detection_to_out(d) for d in detections],
        query=q,
    )
