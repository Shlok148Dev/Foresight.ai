"""
Foresight — Performance Monitoring & Metrics
==============================================
Prometheus metrics endpoint + middleware for request tracking.
"""

from fastapi import APIRouter, Request, Response
from prometheus_client import (
    Counter,
    Histogram,
    Gauge,
    generate_latest,
    CONTENT_TYPE_LATEST,
)
import time
import psutil

router = APIRouter(tags=["monitoring"])

# ── Prometheus Metrics ──────────────────────────────────────────

# Request count by method, path, and status code
REQUEST_COUNT = Counter(
    "foresight_http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)

# Request latency histogram (in seconds)
REQUEST_LATENCY = Histogram(
    "foresight_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5],
)

# Active requests gauge
ACTIVE_REQUESTS = Gauge(
    "foresight_http_active_requests",
    "Number of active HTTP requests",
)

# Database query latency
DB_QUERY_LATENCY = Histogram(
    "foresight_db_query_duration_seconds",
    "Database query latency in seconds",
    ["operation"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.5],
)

# Signal processing metrics
SIGNALS_INGESTED = Counter(
    "foresight_signals_ingested_total",
    "Total signals ingested",
    ["platform"],
)

DETECTIONS_CREATED = Counter(
    "foresight_detections_created_total",
    "Total detections created",
)


# ── Middleware ───────────────────────────────────────────────────

async def metrics_middleware(request: Request, call_next):
    """Track request count, latency, and active connections."""
    ACTIVE_REQUESTS.inc()
    start_time = time.perf_counter()

    response = await call_next(request)

    duration = time.perf_counter() - start_time
    path = request.url.path
    method = request.method
    status = str(response.status_code)

    REQUEST_COUNT.labels(method=method, path=path, status_code=status).inc()
    REQUEST_LATENCY.labels(method=method, path=path).observe(duration)
    ACTIVE_REQUESTS.dec()

    # Add server timing header for client-side performance tracking
    response.headers["Server-Timing"] = f"total;dur={duration * 1000:.1f}"

    return response


# ── Endpoints ────────────────────────────────────────────────────

@router.get("/metrics")
async def prometheus_metrics():
    """Prometheus-compatible metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


@router.get("/health/detailed")
async def detailed_health():
    """Detailed health check with system metrics."""
    cpu = psutil.cpu_percent(interval=0.1)
    memory = psutil.virtual_memory()

    return {
        "status": "healthy",
        "system": {
            "cpu_percent": cpu,
            "memory_used_mb": round(memory.used / 1024 / 1024),
            "memory_total_mb": round(memory.total / 1024 / 1024),
            "memory_percent": memory.percent,
        },
        "version": "0.1.0",
    }
