import re
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.dependencies import get_current_user
from app.models import Organization, OrganizationMember, Project, Role, User
from app.schemas import OrganizationCreate, OrganizationRead

router = APIRouter(prefix="/organizations", tags=["Organizations"])


def slugify(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value or "organization"


@router.post("", response_model=OrganizationRead, status_code=201)
async def create_organization(data: OrganizationCreate, user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    slug = data.slug or slugify(data.name)
    if await session.scalar(select(Organization).where(Organization.slug == slug)):
        raise HTTPException(status_code=409, detail="Organization slug is already in use")
    organization = Organization(name=data.name, slug=slug, description=data.description)
    session.add(organization)
    await session.flush()
    session.add(OrganizationMember(organization_id=organization.id, user_id=user.id, role=Role.OWNER))
    await session.commit()
    await session.refresh(organization)
    return organization


@router.get("", response_model=list[OrganizationRead])
async def list_organizations(user: User = Depends(get_current_user), session: AsyncSession = Depends(get_session)):
    return list((await session.scalars(select(Organization).join(OrganizationMember).where(OrganizationMember.user_id == user.id).order_by(Organization.created_at.desc()))).all())
