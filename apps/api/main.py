import json
import logging
import time
from collections import defaultdict, deque
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from sqlalchemy import text

from app.core.logging import configure_logging
from app.core.metrics import collector
from config import settings
from sqlalchemy.orm import Session
from database import SessionLocal, get_db, create_all_tables
import redis

# Logging
configure_logging()
logger = logging.getLogger("ai_commerce")

# Redis client
redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

# Simple in-memory per-IP rate limiter (for single-node deployments)
_request_log: defaultdict[str, deque[float]] = defaultdict(lambda: deque(maxlen=settings.RATE_LIMIT_PER_MINUTE + 1))


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered e-commerce platform API",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    start = time.time()
    path = request.url.path
    method = request.method
    client = request.client.host if request.client else "unknown"
    logger.info("Request started", extra={"method": method, "path": path, "client": client})
    try:
        response = await call_next(request)
    except Exception as exc:
        logger.exception("Request failed", extra={"method": method, "path": path, "client": client})
        raise
    finally:
        pass
    duration_ms = (time.time() - start) * 1000
    status = response.status_code
    collector.record_request(path, method, duration_ms, status)
    logger.info(
        "Request completed",
        extra={"method": method, "path": path, "status": status, "duration_ms": round(duration_ms, 2), "client": client},
    )
    return response


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client = request.client.host if request.client else "unknown"
    now = time.time()
    log = _request_log[client]
    # Drop entries older than 60s
    while log and log[0] < now - 60:
        log.popleft()
    if len(log) >= settings.RATE_LIMIT_PER_MINUTE:
        logger.warning("Rate limit exceeded", extra={"client": client})
        return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})
    log.append(now)
    response = await call_next(request)
    return response


def _check_db() -> dict:
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "ok"}
    except Exception as exc:
        logger.exception("Database health check failed")
        return {"status": "error", "detail": str(exc)}


def _check_redis() -> dict:
    try:
        redis_client.ping()
        return {"status": "ok"}
    except Exception as exc:
        logger.exception("Redis health check failed")
        return {"status": "error", "detail": str(exc)}


@app.get("/health")
async def health_check():
    db_status = _check_db()
    redis_status = _check_redis()
    overall = "healthy" if db_status["status"] == "ok" and redis_status["status"] == "ok" else "unhealthy"
    return {
        "status": overall,
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": db_status,
        "redis": redis_status,
    }


@app.get("/api/v1/admin/system-status")
async def system_status():
    # NOTE: this endpoint is public in RC2 for dashboard convenience.
    # In production, protect it with Depends(get_current_user).
    health = await health_check()
    metrics = collector.get()
    return {
        "health": health,
        "metrics": metrics,
        "environment": {
            "debug": settings.DEBUG,
            "log_level": settings.LOG_LEVEL,
            "rate_limit_per_minute": settings.RATE_LIMIT_PER_MINUTE,
        },
    }


@app.get("/api/v1/validation/report")
async def validation_report():
    """Return the latest generated validation report."""
    root = Path(__file__).resolve().parent.parent.parent
    path = root / "validation" / "report.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Validation report not generated yet")
    return json.loads(path.read_text(encoding="utf-8"))


@app.get("/api/v1/dashboard")
async def dashboard(db: Session = Depends(get_db)):
    """Aggregate dashboard metrics."""
    from app.store_builder.repositories.store_repository import StoreRepository
    from app.billing.service import BillingService

    repo = StoreRepository(db)
    stores, total = repo.list_stores(limit=9999)
    recent = [
        {
            "id": s.id,
            "store_name": s.store_name,
            "validation_score": s.validation_score,
            "created_at": s.created_at.isoformat() if s.created_at else "",
        }
        for s in stores[:6]
    ]
    avg_score = sum(s.validation_score for s in stores) / total if total else 0

    # AI consumption is approximated by the number of AI-heavy launches in metadata
    ai_usage = sum(1 for s in stores if (s.blueprint_json or {}).get("metadata", {}).get("ai_provider_used"))

    # Billing summary (all users on free for now)
    billing = BillingService(db)
    # This is a global summary; in production, aggregate by user.
    plans = {"free": 0, "pro": 0, "business": 0}

    return {
        "total_stores": total,
        "average_validation_score": round(avg_score, 1),
        "recent_stores": recent,
        "ai_usage_count": ai_usage,
        "plan_distribution": plans,
    }


# Include routers
from app.trend_intelligence import router as trend_router
from app.product_intelligence import router as product_router
from app.supplier_intelligence import router as supplier_router
from app.brand_builder import router as brand_router
from app.store_builder import router as store_router
from app.demo import router as demo_router
from app.launch import router as launch_router
from app.stripe_integration import router as stripe_router
from app.auth import router as auth_router

app.include_router(auth_router, prefix="/api/v1")
app.include_router(stripe_router)
app.include_router(trend_router)
app.include_router(product_router)
app.include_router(supplier_router)
app.include_router(brand_router)
app.include_router(store_router)
app.include_router(demo_router)
app.include_router(launch_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.API_PORT)
