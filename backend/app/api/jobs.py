from app.services import jobs
from datetime import datetime, timezone
from uuid import UUID
from zoneinfo import ZoneInfo

from croniter import croniter
from fastapi import APIRouter, Depends, Header, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db import get_session
from app.dependencies import get_current_user
from app.models import DeadLetterJob, Job, JobExecution, JobLog, JobState, JobType, OrganizationMember, Project, Queue, User
from app.schemas import BatchJobCreate, ExecutionRead, JobCreate, JobRead, LogRead, Page
from app.services.jobs import add_log, create_job
from app.websocket import job_ws_manager
from app.websocket import publish_job_update

router = APIRouter(prefix="/jobs", tags=["Jobs"])


async def accessible_queue(
    queue_id: UUID,
    user: User,
    session: AsyncSession,
) -> Queue:

    queue = await session.scalar(
        select(Queue)
        .select_from(Queue)
        .join(
            Project,
            Queue.project_id == Project.id,
        )
        .join(
            OrganizationMember,
            Project.organization_id == OrganizationMember.organization_id,
        )
        .where(
            Queue.id == queue_id,
            OrganizationMember.user_id == user.id,
        )
    )

    if queue is None:
        raise HTTPException(
            status_code=404,
            detail="Queue not found",
        )

    return queue


async def accessible_job(
    job_id: UUID,
    user: User,
    session: AsyncSession,
) -> Job:

    job = await session.scalar(
        select(Job)
        .select_from(Job)
        .options(
            joinedload(Job.queue)
            .joinedload(Queue.retry_policy)
        )
        .join(
            Queue,
            Job.queue_id == Queue.id,
        )
        .join(
            Project,
            Queue.project_id == Project.id,
        )
        .join(
            OrganizationMember,
            Project.organization_id == OrganizationMember.organization_id,
        )
        .where(
            Job.id == job_id,
            OrganizationMember.user_id == user.id,
        )
    )

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    return job

async def serialize_job(job: Job, session: AsyncSession) -> dict:
    dlq = await session.scalar(
        select(DeadLetterJob).where(
            DeadLetterJob.job_id == job.id
        )
    )

    return {
        "id": job.id,
        "queue_id": job.queue_id,
        "task_type": job.task_type,
        "job_type": job.job_type,
        "type": job.job_type,
        "payload": job.payload,
        "priority": job.priority,
        "state": job.state,
        "status": job.state,
        "scheduled_at": job.scheduled_at,
        "available_at": job.available_at,
        "attempts": job.attempts,
        "claimed_at": job.claimed_at,
        "worker_id": job.worker_id,
        "last_error": job.last_error,
        "created_at": job.created_at,
        "started_at": job.started_at,
        "completed_at": job.completed_at,
        "queue_name": job.queue.name if job.queue else None,
        "dead_letter_id": dlq.id if dlq else None,
    }


@router.post("", response_model=JobRead, status_code=201)
async def enqueue_job(
    data: JobCreate,
    idempotency_key: str | None = Header(
        default=None,
        alias="Idempotency-Key",
    ),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    queue = await accessible_queue(
        data.queue_id,
        user,
        session,
    )

    key = idempotency_key or data.idempotency_key

    # ---------------------------------------------------------
    # CRON JOB
    # ---------------------------------------------------------

    if data.type == JobType.CRON:

        if not data.cron_expression:
            raise HTTPException(
                status_code=422,
                detail="cron_expression is required for CRON jobs",
            )

        try:
            tz = ZoneInfo(data.timezone)

            local_now = datetime.now(
                timezone.utc
            ).astimezone(tz)

            next_run = (
                croniter(
                    data.cron_expression,
                    local_now,
                )
                .get_next(datetime)
                .replace(tzinfo=tz)
                .astimezone(timezone.utc)
            )

        except Exception as exc:
            raise HTTPException(
                status_code=422,
                detail=(
                    "Invalid cron expression or timezone: "
                    f"{exc}"
                ),
            ) from exc

        template = await create_job(
            session,
            queue,
            data.task_type,
            data.payload,
            data.priority,
            JobType.CRON,
            scheduled_at=next_run,
            idempotency_key=key,
        )

        template.state = JobState.CANCELLED
        template.is_schedule_template = True

        from app.models import ScheduledJob

        session.add(
            ScheduledJob(
                job_template_id=template.id,
                cron_expression=data.cron_expression,
                timezone=data.timezone,
                next_run_at=next_run,
                enabled=True,
            )
        )

        add_log(
            session,
            template.id,
            "Cron schedule created",
            metadata={
                "cron": data.cron_expression,
                "timezone": data.timezone,
            },
        )

        await session.commit()
        await session.refresh(template)

        await publish_job_update(
            template,
            event="job.created",
        )

        return await serialize_job(
            template,
            session,
        )

    # ---------------------------------------------------------
    # NORMAL / IMMEDIATE / SCHEDULED / DELAYED JOB
    # ---------------------------------------------------------

    job = await create_job(
        session,
        queue,
        data.task_type,
        data.payload,
        data.priority,
        data.type,
        scheduled_at=data.scheduled_at,
        delay_seconds=data.delay_seconds,
        idempotency_key=key,
    )

    await session.commit()
    await session.refresh(job)

    job.queue = queue

    await publish_job_update(
        job,
        event="job.created",
    )

    return await serialize_job(
        job,
        session,
    )

@router.post("/batch", response_model=JobRead, status_code=201)
async def enqueue_batch(data: BatchJobCreate, idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"), user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    queue = await accessible_queue(data.queue_id, user, session)
    parent = await create_job(session, queue, "batch", {"count": len(data.jobs)}, data.priority, JobType.BATCH, idempotency_key=idempotency_key)
    parent.batch_id = parent.id
    for item in data.jobs:
        child = await create_job(session, queue, item.task_type, item.payload, item.priority, JobType.BATCH, idempotency_key=None)
        child.batch_id = parent.id
        child.parent_job_id = parent.id
    parent.state = JobState.COMPLETED
    parent.completed_at = datetime.now(timezone.utc)
    add_log(session, parent.id, "Batch created", metadata={"count": len(data.jobs)})
    await session.commit()
    await session.refresh(parent)
    parent.queue = queue
    return await serialize_job(parent, session)


@router.get("", response_model=Page)
async def list_jobs(
    queue_id: UUID | None = None,
    status: str | None = None,
    q: str | None = None,
    worker_id: UUID | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=200),
    sort: str = "created_at",
    order: str = "desc",
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    filters = [
        OrganizationMember.user_id == user.id,
        Job.is_schedule_template.is_(False),
    ]

    if queue_id:
        filters.append(Job.queue_id == queue_id)

    if status:
        try:
            filters.append(Job.state == JobState(status.upper()))
        except ValueError:
            raise HTTPException(
                status_code=422,
                detail="Invalid job status",
            )

    if worker_id:
        filters.append(Job.worker_id == worker_id)

    if q:
        filters.append(
            Job.task_type.ilike(f"%{q}%")
        )

    # -----------------------------
    # TOTAL COUNT
    # -----------------------------

    total = await session.scalar(
        select(func.count(Job.id))
        .select_from(Job)
        .join(
            Queue,
            Job.queue_id == Queue.id,
        )
        .join(
            Project,
            Queue.project_id == Project.id,
        )
        .join(
            OrganizationMember,
            Project.organization_id == OrganizationMember.organization_id,
        )
        .where(*filters)
    ) or 0

    # -----------------------------
    # SORTING
    # -----------------------------

    order_col = (
        Job.created_at
        if sort != "priority"
        else Job.priority
    )

    order_expr = (
        order_col.asc()
        if order.lower() == "asc"
        else order_col.desc()
    )

    # -----------------------------
    # FETCH JOBS
    # -----------------------------

    result = await session.scalars(
        select(Job)
        .select_from(Job)
        .options(
            joinedload(Job.queue)
        )
        .join(
            Queue,
            Job.queue_id == Queue.id,
        )
        .join(
            Project,
            Queue.project_id == Project.id,
        )
        .join(
            OrganizationMember,
            Project.organization_id == OrganizationMember.organization_id,
        )
        .where(*filters)
        .order_by(order_expr)
        .offset((page - 1) * limit)
        .limit(limit)
    )

    rows = list(result.all())

    return Page(
        items=[
            await serialize_job(job, session)
            for job in rows
        ],
        page=page,
        limit=limit,
        total=total,
    )

@router.get("/{job_id}", response_model=JobRead)
async def get_job(job_id: UUID, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return await serialize_job(await accessible_job(job_id, user, session), session)


@router.get("/{job_id}/executions", response_model=list[ExecutionRead])
async def executions(job_id: UUID, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    await accessible_job(job_id, user, session)
    return list((await session.scalars(select(JobExecution).where(JobExecution.job_id == job_id).order_by(JobExecution.attempt_number))).all())


@router.get("/{job_id}/logs", response_model=list[LogRead])
async def logs(job_id: UUID, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    await accessible_job(job_id, user, session)
    return list((await session.scalars(select(JobLog).where(JobLog.job_id == job_id).order_by(JobLog.timestamp))).all())


@router.post("/{job_id}/retry", response_model=JobRead)
async def retry_job(job_id: UUID, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    job = await accessible_job(job_id, user, session)
    if job.state not in [JobState.FAILED, JobState.DEAD_LETTER]:
        raise HTTPException(status_code=409, detail="Only failed or dead-letter jobs can be retried")
    dlq = await session.scalar(select(DeadLetterJob).where(DeadLetterJob.job_id == job.id))
    if dlq: await session.delete(dlq)
    job.state = JobState.QUEUED
    job.available_at = datetime.now(timezone.utc)
    job.attempts = 0
    job.worker_id = None
    job.last_error = None
    add_log(session, job.id, "Job manually retried")
    await session.commit()
    await session.refresh(job)
    await publish_job_update(
        job,
        event="job.updated",
    )
    return await serialize_job(job, session)


@router.post("/{job_id}/cancel", response_model=JobRead)
async def cancel_job(job_id: UUID, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    job = await accessible_job(job_id, user, session)
    if job.state in [JobState.COMPLETED, JobState.CANCELLED, JobState.DEAD_LETTER]:
        raise HTTPException(status_code=409, detail="Job cannot be cancelled in its current state")
    job.state = JobState.CANCELLED
    job.worker_id = None
    add_log(session, job.id, "Job cancelled", level="WARNING")
    await session.commit()
    await session.refresh(job)

    await publish_job_update(
        job,
        event="job.updated",
    )
    return await serialize_job(job, session)


@router.websocket("/ws")
async def jobs_websocket(websocket: WebSocket) -> None:
    await job_ws_manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        job_ws_manager.disconnect(websocket)
    except Exception:
        job_ws_manager.disconnect(websocket)