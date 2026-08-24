from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, literal_column, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.dependencies import get_current_user
from app.models import (
    Job,
    JobState,
    OrganizationMember,
    Project,
    Queue,
    User,
    Worker,
    WorkerStatus,
)


router = APIRouter(
    prefix="/metrics",
    tags=["Metrics"],
)


@router.get("/overview")
async def overview(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    scope = OrganizationMember.user_id == user.id

    total_queues = await session.scalar(
        select(func.count(Queue.id))
        .select_from(Queue)
        .join(
            Project,
            Queue.project_id == Project.id,
        )
        .join(
            OrganizationMember,
            Project.organization_id
            == OrganizationMember.organization_id,
        )
        .where(scope)
    ) or 0

    job_counts_result = await session.execute(
        select(
            Job.state,
            func.count(Job.id),
        )
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
            Project.organization_id
            == OrganizationMember.organization_id,
        )
        .where(scope)
        .group_by(Job.state)
    )

    job_counts = dict(job_counts_result.all())

    workers = list(
        (
            await session.scalars(
                select(Worker)
            )
        ).all()
    )

    now = datetime.now(timezone.utc)

    for worker in workers:
        if worker.last_heartbeat_at is None:
            worker.status = WorkerStatus.OFFLINE
            continue

        if (
            now - worker.last_heartbeat_at
        ).total_seconds() > 30:
            worker.status = WorkerStatus.OFFLINE

    await session.commit()

    completed = job_counts.get(
        JobState.COMPLETED,
        0,
    )

    failed = job_counts.get(
        JobState.FAILED,
        0,
    )

    queued = job_counts.get(
        JobState.QUEUED,
        0,
    )

    running = (
        job_counts.get(
            JobState.RUNNING,
            0,
        )
        + job_counts.get(
            JobState.CLAIMED,
            0,
        )
    )

    dlq = job_counts.get(
        JobState.DEAD_LETTER,
        0,
    )

    active_workers = sum(
        1
        for worker in workers
        if worker.status == WorkerStatus.ONLINE
    )

    offline_workers = sum(
        1
        for worker in workers
        if worker.status == WorkerStatus.OFFLINE
    )

    utilization = [
        {
            "name": worker.worker_key,
            "running": worker.current_job_count or 0,
            "utilization": (
                round(
                    (
                        (worker.current_job_count or 0)
                        / worker.max_concurrency
                    )
                    * 100,
                    1,
                )
                if worker.max_concurrency
                else 0
            ),
        }
        for worker in workers
    ]

    queue_depth_result = await session.execute(
        select(
            Queue.name,
            func.count(Job.id).filter(
                Job.state == JobState.QUEUED
            ),
        )
        .select_from(Queue)
        .join(
            Project,
            Queue.project_id == Project.id,
        )
        .join(
            OrganizationMember,
            Project.organization_id
            == OrganizationMember.organization_id,
        )
        .outerjoin(
            Job,
            Job.queue_id == Queue.id,
        )
        .where(scope)
        .group_by(
            Queue.id,
            Queue.name,
        )
        .order_by(
            func.count(Job.id)
            .filter(Job.state == JobState.QUEUED)
            .desc()
        )
        .limit(10)
    )

    queue_depth = [
        {
            "name": name,
            "queued": count,
        }
        for name, count in queue_depth_result.all()
    ]

    now_hour = now - timedelta(hours=1)

    throughput = await session.scalar(
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
            Project.organization_id
            == OrganizationMember.organization_id,
        )
        .where(
            scope,
            Job.state == JobState.COMPLETED,
            Job.completed_at >= now_hour,
        )
    ) or 0

    start_time = now - timedelta(hours=24)

    hour = literal_column("'hour'")

    completed_bucket = func.date_trunc(
        hour,
        Job.completed_at,
    ).label("bucket")

    completed_series_result = await session.execute(
        select(
            completed_bucket,
            func.count(Job.id),
        )
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
            Project.organization_id
            == OrganizationMember.organization_id,
        )
        .where(
            scope,
            Job.state == JobState.COMPLETED,
            Job.completed_at.is_not(None),
            Job.completed_at >= start_time,
        )
        .group_by(completed_bucket)
        .order_by(completed_bucket)
    )

    failed_bucket = func.date_trunc(
        hour,
        Job.updated_at,
    ).label("bucket")

    failed_series_result = await session.execute(
        select(
            failed_bucket,
            func.count(Job.id),
        )
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
            Project.organization_id
            == OrganizationMember.organization_id,
        )
        .where(
            scope,
            Job.state == JobState.FAILED,
            Job.updated_at.is_not(None),
            Job.updated_at >= start_time,
        )
        .group_by(failed_bucket)
        .order_by(failed_bucket)
    )

    completed_series = {
        bucket: count
        for bucket, count in completed_series_result.all()
    }

    failed_series = {
        bucket: count
        for bucket, count in failed_series_result.all()
    }

    jobs_over_time = []

    current_bucket = start_time.replace(
        minute=0,
        second=0,
        microsecond=0,
    )

    end_bucket = now.replace(
        minute=0,
        second=0,
        microsecond=0,
    )

    while current_bucket <= end_bucket:
        jobs_over_time.append(
            {
                "label": current_bucket.strftime("%H:%M"),
                "completed": completed_series.get(
                    current_bucket,
                    0,
                ),
                "failed": failed_series.get(
                    current_bucket,
                    0,
                ),
            }
        )

        current_bucket += timedelta(hours=1)

    throughput_series = [
        {
            "label": item["label"],
            "completed": item["completed"],
            "failed": item["failed"],
        }
        for item in jobs_over_time
    ]

    return {
        "total_queues": total_queues,
        "queued_jobs": queued,
        "running_jobs": running,
        "completed_jobs": completed,
        "failed_jobs": failed,
        "dlq_jobs": dlq,
        "active_workers": active_workers,
        "offline_workers": offline_workers,
        "throughput": throughput,
        "jobs_over_time": jobs_over_time,
        "throughput_series": throughput_series,
        "queue_depth": queue_depth,
        "worker_utilization": utilization,
        "success_failure": [
            {
                "name": "Completed",
                "value": completed,
            },
            {
                "name": "Failed",
                "value": failed,
            },
        ],
    }