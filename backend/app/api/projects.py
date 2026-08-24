import re
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.db import get_session
from app.dependencies import get_current_user, require_member
from app.models import Job, OrganizationMember, Project, Queue, User
from app.schemas import ProjectCreate, ProjectPatch, ProjectRead


router = APIRouter(prefix="/projects", tags=["Projects"])


def slugify(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value or "project"


async def project_or_404(
    project_id: UUID,
    user: User,
    session: AsyncSession,
) -> Project:
    project = await session.scalar(
        select(Project)
        .select_from(Project)
        .join(
            OrganizationMember,
            OrganizationMember.organization_id == Project.organization_id,
        )
        .where(
            Project.id == project_id,
            OrganizationMember.user_id == user.id,
        )
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    return project


async def project_payload(
    project: Project,
    session: AsyncSession,
) -> dict:
    rows = await session.execute(
        select(Job.state, func.count(Job.id))
        .join(
            Queue,
            Job.queue_id == Queue.id,
        )
        .where(
            Queue.project_id == project.id,
        )
        .group_by(Job.state)
    )

    counts = {
        state.value.lower(): count
        for state, count in rows.all()
    }

    return {
        "id": project.id,
        "organization_id": project.organization_id,
        "organization_name": project.organization.name if project.organization else None,
        "name": project.name,
        "slug": project.slug,
        "description": project.description,
        "created_at": project.created_at,
        "organization_name": (
            project.organization.name
            if project.organization
            else None
        ),
        "job_counts": {
            "queued": counts.get("queued", 0),
            "running": (
                counts.get("running", 0)
                + counts.get("claimed", 0)
            ),
            "completed": counts.get("completed", 0),
            "failed": counts.get("failed", 0),
        },
    }


@router.post(
    "",
    response_model=ProjectRead,
    status_code=201,
)
async def create_project(
    data: ProjectCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await require_member(
        data.organization_id,
        user,
        session,
    )

    slug = data.slug or slugify(data.name)

    existing_project = await session.scalar(
        select(Project).where(
            Project.organization_id == data.organization_id,
            Project.slug == slug,
        )
    )

    if existing_project:
        raise HTTPException(
            status_code=409,
            detail="Project slug already exists",
        )

    project = Project(
        organization_id=data.organization_id,
        name=data.name,
        slug=slug,
        description=data.description,
    )

    session.add(project)

    await session.commit()
    await session.refresh(project)

    return project


@router.get("")
async def list_projects(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):

    total = await session.scalar(
        select(func.count(Project.id))
        .select_from(Project)
        .join(
            OrganizationMember,
            OrganizationMember.organization_id == Project.organization_id,
        )
        .where(
            OrganizationMember.user_id == user.id,
        )
    ) or 0

    result = await session.scalars(
        select(Project)
        .select_from(Project)
        .options(
            joinedload(Project.organization)
        )
        .join(
            OrganizationMember,
            OrganizationMember.organization_id == Project.organization_id,
        )
        .where(
            OrganizationMember.user_id == user.id,
        )
        .order_by(
            Project.created_at.desc()
        )
        .offset(
            (page - 1) * limit
        )
        .limit(limit)
    )

    projects = list(result.all())

    return {
        "items": [
            await project_payload(project, session)
            for project in projects
        ],
        "page": page,
        "limit": limit,
        "total": total,
    }


@router.get("/{project_id}")
async def get_project(
    project_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    project = await session.scalar(
        select(Project)
        .select_from(Project)
        .options(
            joinedload(Project.organization)
        )
        .join(
            OrganizationMember,
            OrganizationMember.organization_id == Project.organization_id,
        )
        .where(
            Project.id == project_id,
            OrganizationMember.user_id == user.id,
        )
    )

    if project is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    return await project_payload(
        project,
        session,
    )


@router.patch("/{project_id}")
async def patch_project(
    project_id: UUID,
    data: ProjectPatch,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    project = await project_or_404(
        project_id,
        user,
        session,
    )

    if data.name is not None:
        project.name = data.name

    if data.description is not None:
        project.description = data.description

    await session.commit()
    await session.refresh(project)

    return project


@router.delete(
    "/{project_id}",
    status_code=204,
)
async def delete_project(
    project_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    project = await project_or_404(
        project_id,
        user,
        session,
    )

    await session.delete(project)
    await session.commit()