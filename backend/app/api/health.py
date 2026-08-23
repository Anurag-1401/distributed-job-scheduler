from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import get_settings
from app.db import get_engine
from app.runtime import runtime

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health():
    return {"status": "ok", "service": "distributed-job-scheduler"}


@router.get("/ready")
async def ready():
    database = "healthy"
    redis = "healthy"
    scheduler = "healthy"
    workers = "healthy"
    try:
        async with get_engine().connect() as connection:
            await connection.execute(text("SELECT 1"))
    except Exception:
        database = "unhealthy"
    try:
        await runtime.redis.ping()
    except Exception:
        redis = "unhealthy"
    if runtime.tasks and runtime.scheduler.stop_event.is_set():
        scheduler = "unhealthy"
    if not runtime.workers or all(worker.stop_event.is_set() for worker in runtime.workers):
        workers = "unhealthy"
    status = "ready" if database == redis == scheduler == workers == "healthy" else "not_ready"
    return {"status": status, "database": database, "postgresql": database, "redis": redis, "scheduler": scheduler, "workers": workers}
