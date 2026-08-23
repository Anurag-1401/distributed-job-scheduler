import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import (
    DeadLetterJob,
    Job,
    JobExecution,
    JobLog,
    JobState,
    JobType,
    Queue,
    QueueStatus,
    RetryPolicy,
    Worker,
)
from app.services.retry import retry_delay

logger = logging.getLogger(__name__)


def add_log(
    session: AsyncSession,
    job_id: UUID,
    message: str,
    level: str = "INFO",
    execution_id: UUID | None = None,
    metadata: dict | None = None,
) -> None:
    session.add(
        JobLog(
            job_id=job_id,
            execution_id=execution_id,
            level=level,
            message=message,
            metadata_json=metadata,
        )
    )


async def create_job(
    session: AsyncSession,
    queue: Queue,
    task_type: str,
    payload: dict,
    priority: int,
    job_type: JobType = JobType.IMMEDIATE,
    scheduled_at: datetime | None = None,
    delay_seconds: float | None = None,
    idempotency_key: str | None = None,
) -> Job:

    if idempotency_key:
        existing = await session.scalar(
            select(Job).where(
                Job.queue_id == queue.id,
                Job.idempotency_key == idempotency_key,
            )
        )

        if existing:
            return existing

    now = datetime.now(timezone.utc)

    if delay_seconds is not None:
        scheduled_at = now + timedelta(seconds=delay_seconds)

    state = (
        JobState.SCHEDULED
        if scheduled_at and scheduled_at > now
        else JobState.QUEUED
    )

    job = Job(
        queue_id=queue.id,
        task_type=task_type,
        job_type=job_type,
        payload=payload,
        priority=priority,
        scheduled_at=scheduled_at,
        available_at=scheduled_at or now,
        state=state,
        idempotency_key=idempotency_key,
    )

    session.add(job)
    await session.flush()

    add_log(
        session,
        job.id,
        "Job created",
        metadata={
            "type": job_type.value,
            "task_type": task_type,
            "priority": priority,
        },
    )

    logger.info(
        "JOB CREATED | id=%s | queue=%s | state=%s",
        job.id,
        queue.id,
        state.value,
    )

    return job


async def claim_job(
    session: AsyncSession,
    worker: Worker,
) -> Job | None:
    now = datetime.now(timezone.utc)

    # ---------------------------------------------------------
    # 1. Worker capacity
    # ---------------------------------------------------------
    active_count = await session.scalar(
        select(func.count(Job.id)).where(
            Job.worker_id == worker.id,
            Job.state.in_(
                [
                    JobState.CLAIMED,
                    JobState.RUNNING,
                ]
            ),
        )
    ) or 0

    if active_count >= worker.max_concurrency:
        return None

    # ---------------------------------------------------------
    # 2. Find ONE eligible job ID
    #
    # Important:
    # This SELECT only finds the candidate.
    # It does NOT claim the job.
    # ---------------------------------------------------------
    candidate_query = (
        select(Job.id)
        .join(
            Queue,
            Job.queue_id == Queue.id,
        )
        .where(
            Queue.status == QueueStatus.ACTIVE,
            Job.state.in_(
                [
                    JobState.QUEUED,
                    JobState.RETRYING,
                ]
            ),
            Job.available_at <= now,
            Job.is_schedule_template.is_(False),
        )
        .order_by(
            Job.priority.desc(),
            Job.created_at.asc(),
        )
        .limit(1)
    )

    job_id = await session.scalar(candidate_query)

    if job_id is None:
        return None

    # ---------------------------------------------------------
    # 3. ATOMIC CLAIM
    #
    # The state condition is critical.
    #
    # If another worker already claimed this job, this UPDATE
    # affects 0 rows and this worker gets None.
    # ---------------------------------------------------------
    claim_query = (
        update(Job)
        .where(
            Job.id == job_id,
            Job.state.in_(
                [
                    JobState.QUEUED,
                    JobState.RETRYING,
                ]
            ),
        )
        .values(
            state=JobState.CLAIMED,
            worker_id=worker.id,
            claimed_at=now,
            attempts=Job.attempts + 1,
        )
        .returning(Job.id)
    )

    result = await session.execute(claim_query)

    claimed_id = result.scalar_one_or_none()

    if claimed_id is None:
        # Another worker won the race.
        return None

    # ---------------------------------------------------------
    # 4. Load the claimed job
    # ---------------------------------------------------------
    job = await session.scalar(
        select(Job)
        .options(
            joinedload(Job.queue).joinedload(
                Queue.retry_policy
            )
        )
        .where(Job.id == claimed_id)
    )

    if job is None:
        return None

    # ---------------------------------------------------------
    # 5. Update worker count
    # ---------------------------------------------------------
    worker.current_job_count += 1

    add_log(
        session,
        job.id,
        "Job claimed",
        metadata={
            "worker_id": str(worker.id),
            "worker_key": worker.worker_key,
            "attempt": job.attempts,
        },
    )

    logger.info(
        "JOB CLAIMED | job=%s | worker=%s | attempt=%s",
        job.id,
        worker.worker_key,
        job.attempts,
    )

    return job

async def start_execution(
    session: AsyncSession,
    job: Job,
    worker: Worker,
) -> JobExecution:

    now = datetime.now(timezone.utc)

    job.state = JobState.RUNNING
    job.started_at = now

    execution = JobExecution(
        job_id=job.id,
        worker_id=worker.id,
        attempt_number=job.attempts,
        status="RUNNING",
        started_at=now,
    )

    session.add(execution)
    await session.flush()

    add_log(
        session,
        job.id,
        "Execution started",
        execution_id=execution.id,
        metadata={
            "attempt": job.attempts,
            "worker_id": str(worker.id),
        },
    )

    logger.info(
        "EXECUTION STARTED | job=%s | execution=%s | worker=%s",
        job.id,
        execution.id,
        worker.worker_key,
    )

    return execution


async def finish_execution(
    session: AsyncSession,
    job: Job,
    execution: JobExecution,
    success: bool,
    result: dict | None = None,
    error: str | None = None,
) -> None:

    now = datetime.now(timezone.utc)

    execution.completed_at = now
    execution.duration_ms = max(
        0,
        int(
            (now - execution.started_at).total_seconds() * 1000
        ),
    )

    execution.result_metadata = result
    execution.error = error
    execution.status = "COMPLETED" if success else "FAILED"

    # ---------------------------------------------------------
    # SUCCESS
    # ---------------------------------------------------------

    if success:

        job.state = JobState.COMPLETED
        job.completed_at = now
        job.last_error = None

        add_log(
            session,
            job.id,
            "Job completed",
            execution_id=execution.id,
            metadata={
                "duration_ms": execution.duration_ms,
                "result": result,
            },
        )

        logger.info(
            "JOB COMPLETED | job=%s | execution=%s | duration=%sms",
            job.id,
            execution.id,
            execution.duration_ms,
        )

        return

    # ---------------------------------------------------------
    # FAILURE
    # ---------------------------------------------------------

    policy: RetryPolicy | None = job.queue.retry_policy

    job.last_error = error
    job.worker_id = None

    add_log(
        session,
        job.id,
        "Execution failed",
        level="ERROR",
        execution_id=execution.id,
        metadata={
            "error": error,
            "attempt": job.attempts,
        },
    )

    if policy is None:

        job.state = JobState.DEAD_LETTER

        session.add(
            DeadLetterJob(
                job_id=job.id,
                failure_reason="retry_policy_missing",
                final_error=error or "unknown error",
                attempts=job.attempts,
                worker_id=execution.worker_id,
            )
        )

        logger.error(
            "JOB DEAD LETTER | retry policy missing | job=%s",
            job.id,
        )

        return

    # ---------------------------------------------------------
    # RETRY
    # ---------------------------------------------------------

    if job.attempts < policy.max_attempts:

        delay = retry_delay(
            policy,
            job.attempts,
        )

        job.state = JobState.RETRYING
        job.available_at = now + timedelta(
            seconds=delay
        )

        add_log(
            session,
            job.id,
            "Retry scheduled",
            level="WARNING",
            execution_id=execution.id,
            metadata={
                "delay_seconds": delay,
                "attempt": job.attempts,
            },
        )

        logger.warning(
            "JOB RETRYING | job=%s | attempt=%s | delay=%ss",
            job.id,
            job.attempts,
            delay,
        )

        return

    # ---------------------------------------------------------
    # DEAD LETTER
    # ---------------------------------------------------------

    job.state = JobState.DEAD_LETTER

    session.add(
        DeadLetterJob(
            job_id=job.id,
            failure_reason="retry_exhausted",
            final_error=error or "unknown error",
            attempts=job.attempts,
            worker_id=execution.worker_id,
        )
    )

    add_log(
        session,
        job.id,
        "Job moved to dead letter queue",
        level="ERROR",
        execution_id=execution.id,
        metadata={
            "attempts": job.attempts,
        },
    )

    logger.error(
        "JOB DEAD LETTER | job=%s | attempts=%s",
        job.id,
        job.attempts,
    )


async def recover_abandoned_jobs(
    session: AsyncSession,
    lease_timeout_seconds: int,
) -> int:

    cutoff = (
        datetime.now(timezone.utc)
        - timedelta(seconds=lease_timeout_seconds)
    )

    stale_jobs = list(
        (
            await session.scalars(
                select(Job)
                .options(
                    joinedload(Job.queue).joinedload(
                        Queue.retry_policy
                    )
                )
                .where(
                    Job.state.in_(
                        [
                            JobState.CLAIMED,
                            JobState.RUNNING,
                        ]
                    ),
                    Job.claimed_at < cutoff,
                )
            )
        ).all()
    )

    recovered = 0

    for job in stale_jobs:

        execution = await session.scalar(
            select(JobExecution)
            .where(
                JobExecution.job_id == job.id,
                JobExecution.status == "RUNNING",
            )
            .order_by(
                JobExecution.attempt_number.desc()
            )
        )

        now = datetime.now(timezone.utc)

        if execution:

            execution.status = "FAILED"
            execution.completed_at = now
            execution.duration_ms = max(
                0,
                int(
                    (now - execution.started_at)
                    .total_seconds()
                    * 1000
                ),
            )
            execution.error = "Worker lease expired"

            add_log(
                session,
                job.id,
                "Worker lease expired; execution recovered",
                level="WARNING",
                execution_id=execution.id,
            )

        worker_id = (
            execution.worker_id
            if execution
            else job.worker_id
        )

        job.worker_id = None

        policy = job.queue.retry_policy

        if (
            policy is None
            or job.attempts >= policy.max_attempts
        ):

            job.state = JobState.DEAD_LETTER

            session.add(
                DeadLetterJob(
                    job_id=job.id,
                    failure_reason="worker_timeout",
                    final_error="Worker lease expired",
                    attempts=job.attempts,
                    worker_id=worker_id,
                )
            )

        else:

            job.state = JobState.RETRYING
            job.available_at = now

        recovered += 1

    return recovered