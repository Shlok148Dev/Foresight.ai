"""
Foresight Backend — FastAPI Application Entry Point
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from datetime import datetime
import logging, json, os

from app.db.database import init_db, close_db
from app.api.auth import router as auth_router
from app.api.signals import router as signals_router
from app.api.monitoring import router as monitoring_router, metrics_middleware


class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname, "logger": record.name,
            "message": record.getMessage(), "module": record.module,
        })

def setup_logging():
    logger = logging.getLogger("foresight")
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Foresight backend starting...")
    await init_db()
    yield
    logger.info("Foresight backend shutting down...")
    await close_db()


app = FastAPI(
    title="Foresight API",
    description="AI-powered trend intelligence — detect emerging trends before they go mainstream.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request, call_next):
    start = datetime.utcnow()
    response = await call_next(request)
    ms = (datetime.utcnow() - start).total_seconds() * 1000
    logger.info(f"{request.method} {request.url.path} -> {response.status_code} ({ms:.1f}ms)")
    return response


# ── Routes ──
app.include_router(auth_router, prefix="/api/v1")
app.include_router(signals_router, prefix="/api/v1")
app.include_router(monitoring_router)
app.middleware("http")(metrics_middleware)


@app.get("/health", tags=["system"])
async def health():
    return {"status": "healthy", "version": "0.1.0", "timestamp": datetime.utcnow().isoformat() + "Z"}


@app.get("/", tags=["system"])
async def root():
    return {"service": "Foresight API", "version": "0.1.0", "docs": "/docs"}
