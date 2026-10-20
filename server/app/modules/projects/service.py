from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import DomainError
from app.db.base import now
from app.modules.jobs.models import EditJob
from app.modules.projects import repository
from app.modules.projects.models import Project
from app.modules.projects.schemas import ProjectCreate, ProjectUpdate
from app.modules.users.models import User


async def require_project(
    session: AsyncSession, project_id: UUID, owner_id: UUID, lock: bool = False
) -> Project:
    project = await repository.owned(session, project_id, owner_id, lock)
    if not project:
        raise DomainError("project_not_found", "Project not found", 404)
    return project


async def create(session: AsyncSession, owner_id: UUID, data: ProjectCreate) -> Project:
    await session.scalar(select(User).where(User.id == owner_id).with_for_update())
    count = await session.scalar(
        select(func.count())
        .select_from(Project)
        .where(Project.owner_id == owner_id, Project.deleted_at.is_(None))
    )
    if (count or 0) >= get_settings().max_projects_per_user:
        raise DomainError("project_quota", "Project limit reached", 429)
    project = Project(owner_id=owner_id, **data.model_dump())
    session.add(project)
    await session.flush()
    return project


async def update(
    session: AsyncSession, project_id: UUID, owner_id: UUID, data: ProjectUpdate
) -> Project:
    project = await require_project(session, project_id, owner_id, True)
    if project.revision != data.revision:
        raise DomainError("revision_conflict", "Project changed; reload and retry", 409)
    for key, value in data.model_dump(exclude_unset=True, exclude={"revision"}).items():
        if key == "name" and value is None:
            raise DomainError("invalid_name", "Name cannot be null")
        setattr(project, key, value)
    project.revision += 1
    await session.flush()
    return project


async def delete(session: AsyncSession, project_id: UUID, owner_id: UUID) -> None:
    project = await require_project(session, project_id, owner_id, True)
    active = await session.scalar(
        select(EditJob.id)
        .where(
            EditJob.project_id == project.id,
            EditJob.status.in_(["pending", "queued", "processing", "cancelling"]),
        )
        .limit(1)
    )
    if active:
        raise DomainError("project_busy", "Cancel active jobs before deleting the project", 409)
    project.deleted_at, project.status = now(), "deleted"
