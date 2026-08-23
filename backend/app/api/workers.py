from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db import get_session
from app.dependencies import get_current_user
from app.models import Job, JobState, OrganizationMember, Project, Queue, User, Worker, WorkerStatus
from app.schemas import JobRead, Page, WorkerRead
from app.api.jobs import serialize_job

router = APIRouter(prefix="/workers", tags=["Workers"])


def worker_status(worker: Worker) -> WorkerStatus:
    if (datetime.now(timezone.utc) - worker.last_heartbeat_at).total_seconds() > 30:
        return WorkerStatus.OFFLINE
    return worker.status


async def worker_or_404(worker_id: UUID, session: AsyncSession) -> Worker:
    worker = await session.get(Worker, worker_id)
    if worker is None:
        raise HTTPException(status_code=404, detail="Worker not found")
    return worker


async def worker_payload(worker: Worker, session: AsyncSession) -> dict:
    completed = await session.scalar(select(func.count(Job.id)).where(Job.worker_id == worker.id, Job.state == JobState.COMPLETED)) or 0
    failed = await session.scalar(select(func.count(Job.id)).where(Job.worker_id == worker.id, Job.state == JobState.FAILED)) or 0
    running = worker.current_job_count
    utilization = round((running / worker.max_concurrency) * 100, 1) if worker.max_concurrency else 0
    status = worker_status(worker)
    if status != worker.status:
        worker.status = status
        await session.commit()
    return {"id": worker.id, "worker_key": worker.worker_key, "status": status.value, "max_concurrency": worker.max_concurrency, "concurrency": worker.max_concurrency, "current_job_count": running, "last_heartbeat_at": worker.last_heartbeat_at, "utilization": utilization, "completed_jobs": completed, "failed_jobs": failed, "uptime": "—", "metadata": worker.metadata_json or {}}


@router.get("")
async def list_workers(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    total = await session.scalar(select(func.count(Worker.id))) or 0
    workers = list((await session.scalars(select(Worker).order_by(Worker.last_heartbeat_at.desc()).offset((page - 1) * limit).limit(limit))).all())
    return {"items": [await worker_payload(w, session) for w in workers], "page": page, "limit": limit, "total": total}


@router.get("/{worker_id}")
async def get_worker(worker_id: UUID, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await worker_payload(await worker_or_404(worker_id, session), session)


@router.get("/{worker_id}/jobs", response_model=Page)
async def list_worker_jobs(worker_id: UUID, page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100), user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    await worker_or_404(worker_id, session)
    filters = [Job.worker_id == worker_id, Job.state.in_([JobState.CLAIMED, JobState.RUNNING])]
    total = await session.scalar(select(func.count(Job.id)).where(*filters)) or 0
    jobs = list((await session.scalars(select(Job).options(joinedload(Job.queue)).where(*filters).order_by(Job.started_at.desc()).offset((page - 1) * limit).limit(limit))).all())
    return Page(items=[await serialize_job(job, session) for job in jobs], page=page, limit=limit, total=total)
