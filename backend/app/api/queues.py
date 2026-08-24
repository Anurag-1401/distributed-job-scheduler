from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db import get_session
from app.dependencies import get_current_user
from app.models import (
    Job,
    OrganizationMember,
    Project,
    Queue,
    QueueStatus,
    RetryPolicy,
    User,
)
from app.schemas import QueueCreate, QueuePatch, QueueRead, RetryPolicyRead


router = APIRouter(prefix="/queues", tags=["Queues"])


async def queue_or_404(
    queue_id: UUID,
    user: User,
    session: AsyncSession,
) -> Queue:
    stmt = (
        select(Queue)
        .join(
            Project,
            Queue.project_id == Project.id,
        )
        .join(
            OrganizationMember,
            Project.organization_id
            == OrganizationMember.organization_id,
        )
       .options(
            joinedload(Queue.project),
            joinedload(Queue.retry_policy),
        )
        .where(
            Queue.id == queue_id,
            OrganizationMember.user_id == user.id,
        )
    )

    queue = await session.scalar(stmt)

    if queue is None:
        raise HTTPException(
            status_code=404,
            detail="Queue not found",
        )

    return queue


async def queue_response(
    queue: Queue,
    session: AsyncSession,
) -> dict:
    result = await session.execute(
        select(
            Job.state,
            func.count(Job.id),
        )
        .where(Job.queue_id == queue.id)
        .group_by(Job.state)
    )

    counts = dict(result.all())

    values = {
        state.value: count
        for state, count in counts.items()
    }

    retry_policy = None

    if queue.retry_policy is not None:
        retry_policy = RetryPolicyRead.model_validate(
            queue.retry_policy,
            from_attributes=True,
        )

    return {
        "id": queue.id,
        "project_id": queue.project_id,
        "project_name": queue.project.name if queue.project else None,
        "name": queue.name,
        "priority": queue.priority,
        "concurrency_limit": queue.concurrency_limit,
        "status": queue.status,
        "retry_policy_id": (
            queue.retry_policy.id
            if queue.retry_policy is not None
            else None
        ),
        "retry_policy": retry_policy,
        "stats": {
            "queued_jobs": values.get("QUEUED", 0),
            "scheduled_jobs": values.get("SCHEDULED", 0),
            "running_jobs": (
                values.get("RUNNING", 0)
                + values.get("CLAIMED", 0)
            ),
            "completed_jobs": values.get("COMPLETED", 0),
            "failed_jobs": values.get("FAILED", 0),
            "dlq_jobs": values.get("DEAD_LETTER", 0),
        },
    }

@router.post(
    "",
    response_model=QueueRead,
    status_code=201,
)
async def create_queue(
    data: QueueCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    project_stmt = (
        select(Project)
        .join(
            OrganizationMember,
            Project.organization_id
            == OrganizationMember.organization_id,
        )
        .where(
            Project.id == data.project_id,
            OrganizationMember.user_id == user.id,
        )
    )

    project = await session.scalar(project_stmt)

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    existing_stmt = select(Queue).where(
        Queue.project_id == data.project_id,
        Queue.name == data.name,
    )

    existing = await session.scalar(existing_stmt)

    if existing is not None:
        raise HTTPException(
            status_code=409,
            detail="Queue name already exists in this project",
        )

    queue = Queue(
        project_id=data.project_id,
        name=data.name,
        priority=data.priority,
        concurrency_limit=data.concurrency_limit,
        status=QueueStatus.ACTIVE,
    )

    session.add(queue)

    await session.flush()

    policy_data = data.retry_policy.model_dump()

    policy = RetryPolicy(
        queue_id=queue.id,
        **policy_data,
    )

    session.add(policy)

    await session.commit()

    result = await session.execute(
        select(Queue)
        .options(
            joinedload(Queue.project),
            joinedload(Queue.retry_policy),
        )
        .where(Queue.id == queue.id)
    )

    queue = result.unique().scalar_one()

    return await queue_response(
        queue,
        session,
    )


@router.get("")
async def list_queues(
    project_id: UUID | None = None,
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

    if project_id is not None:
        filters.append(
            Queue.project_id == project_id,
        )

    total_stmt = (
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
        .where(*filters)
    )

    total = (
        await session.scalar(total_stmt)
        or 0
    )

    queues_stmt = (
        select(Queue)
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
        .options(
            joinedload(Queue.project),
            joinedload(Queue.retry_policy),
        )
        .where(*filters)
        .order_by(
            Queue.created_at.desc(),
        )
        .offset(
            (page - 1) * limit,
        )
        .limit(limit)
    )

    result = await session.execute(queues_stmt)

    queues = result.unique().scalars().all()

    return {
        "items": [
            await queue_response(
                queue,
                session,
            )
            for queue in queues
        ],
        "page": page,
        "limit": limit,
        "total": total,
    }


@router.get(
    "/{queue_id}",
)
async def get_queue(
    queue_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    queue = await queue_or_404(
        queue_id,
        user,
        session,
    )

    return await queue_response(
        queue,
        session,
    )


@router.patch(
    "/{queue_id}",
)
async def update_queue(
    queue_id: UUID,
    data: QueuePatch,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    queue = await queue_or_404(
        queue_id,
        user,
        session,
    )

    changes = data.model_dump(
        exclude_unset=True,
    )

    retry = changes.pop(
        "retry_policy",
        None,
    )

    for key, value in changes.items():
        setattr(
            queue,
            key,
            value,
        )

    if retry is not None:
        policy = queue.retry_policy

        if policy is None:
            policy = RetryPolicy(
                queue_id=queue.id,
                **retry,
            )

            session.add(policy)

        else:
            for key, value in retry.items():
                setattr(
                    policy,
                    key,
                    value,
                )

    await session.commit()

    result = await session.execute(
    select(Queue)
    .options(
        joinedload(Queue.project),
        joinedload(Queue.retry_policy),
    )
    .where(Queue.id == queue.id)
)

    queue = result.unique().scalar_one()

    return await queue_response(
        queue,
        session,
    )


@router.post(
    "/{queue_id}/pause",
)
async def pause_queue(
    queue_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    queue = await queue_or_404(
        queue_id,
        user,
        session,
    )

    queue.status = QueueStatus.PAUSED

    await session.commit()

    result = await session.execute(
        select(Queue)
        .options(
            joinedload(Queue.project),
            joinedload(Queue.retry_policy),
        )
        .where(Queue.id == queue.id)
    )

    queue = result.unique().scalar_one()

    return await queue_response(
        queue,
        session,
    )


@router.post(
    "/{queue_id}/resume",
)
async def resume_queue(
    queue_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    queue = await queue_or_404(
        queue_id,
        user,
        session,
    )

    queue.status = QueueStatus.ACTIVE

    await session.commit()

    result = await session.execute(
        select(Queue)
        .options(
            joinedload(Queue.project),
            joinedload(Queue.retry_policy),
        )
        .where(Queue.id == queue.id)
    )

    queue = result.unique().scalar_one()

    return await queue_response(
        queue,
        session,
    )


@router.get(
    "/{queue_id}/stats",
)
async def queue_stats(
    queue_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    queue = await queue_or_404(
        queue_id,
        user,
        session,
    )

    response = await queue_response(
        queue,
        session,
    )

    return response["stats"]