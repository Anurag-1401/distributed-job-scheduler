from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.api.jobs import serialize_job
from app.db import get_session
from app.dependencies import get_current_user
from app.models import (
    DeadLetterJob,
    Job,
    JobState,
    OrganizationMember,
    Project,
    Queue,
    User,
)


router = APIRouter(
    prefix="/dlq",
    tags=["Dead Letter Queue"],
)


async def dlq_access(
    dlq_id: UUID,
    user: User,
    session: AsyncSession,
) -> DeadLetterJob:

    row = await session.scalar(
        select(DeadLetterJob)
        .select_from(DeadLetterJob)
        .join(
            Job,
            DeadLetterJob.job_id == Job.id,
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
            Project.organization_id
            == OrganizationMember.organization_id,
        )
        .where(
            DeadLetterJob.id == dlq_id,
            OrganizationMember.user_id == user.id,
        )
    )

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Dead-letter job not found",
        )

    return row

async def payload(
    row: DeadLetterJob,
    session: AsyncSession,
) -> dict:

    job = await session.scalar(
        select(Job)
        .options(
            joinedload(Job.queue)
        )
        .where(
            Job.id == row.job_id
        )
    )

    return {
        "id": row.id,
        "job_id": row.job_id,

        "queue_id": (
            job.queue_id
            if job
            else None
        ),

        "queue_name": (
            job.queue.name
            if job and job.queue
            else None
        ),

        "final_error": row.final_error,
        "failure_reason": row.failure_reason,
        "attempts": row.attempts,
        "worker_id": row.worker_id,

        "created_at": row.created_at,

        "updated_at": row.created_at,
    }


@router.get("")
async def list_dlq(
    page: int = Query(
        1,
        ge=1,
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
    ),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    filters = [
        OrganizationMember.user_id == user.id,
    ]
 
    total = await session.scalar(
        select(func.count(DeadLetterJob.id))
        .select_from(DeadLetterJob)
        .join(
            Job,
            DeadLetterJob.job_id == Job.id,
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
            Project.organization_id
            == OrganizationMember.organization_id,
        )
        .where(*filters)
    ) or 0

     # Fetch DLQ records
 
    result = await session.scalars(
        select(DeadLetterJob)
        .select_from(DeadLetterJob)
        .join(
            Job,
            DeadLetterJob.job_id == Job.id,
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
            Project.organization_id
            == OrganizationMember.organization_id,
        )
        .where(*filters)
        .order_by(
            DeadLetterJob.created_at.desc()
        )
        .offset(
            (page - 1) * limit
        )
        .limit(limit)
    )

    rows = list(result.all())

     # Response
 
    return {
        "items": [
            await payload(row, session)
            for row in rows
        ],
        "page": page,
        "limit": limit,
        "total": total,
    }


@router.get("/{dlq_id}")
async def get_dlq(
    dlq_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):

    row = await dlq_access(
        dlq_id,
        user,
        session,
    )

    return await payload(
        row,
        session,
    )

@router.post("/{dlq_id}/retry")
async def retry_dlq(
    dlq_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):

    row = await dlq_access(
        dlq_id,
        user,
        session,
    )

 
    job = await session.get(
        Job,
        row.job_id,
    )

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Original job not found",
        )

 
    job.state = JobState.QUEUED

    job.available_at = datetime.now(
        timezone.utc
    )

    job.attempts = 0
    job.worker_id = None
    job.last_error = None
 
    await session.delete(row)

    await session.commit()

    await session.refresh(job)

 
    return await serialize_job(
        job,
        session,
    )
@router.delete(
    "/{dlq_id}",
    status_code=204,
)
async def delete_dlq(
    dlq_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):

    row = await dlq_access(
        dlq_id,
        user,
        session,
    )

    await session.delete(row)

    await session.commit()

    return None