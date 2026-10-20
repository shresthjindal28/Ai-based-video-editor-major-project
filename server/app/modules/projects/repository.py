from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.projects.models import Project


async def owned(
    session: AsyncSession, project_id: UUID, owner_id: UUID, lock: bool = False
) -> Project | None:
    query = select(Project).where(
        Project.id == project_id, Project.owner_id == owner_id, Project.deleted_at.is_(None)
    )
    if lock:
        query = query.with_for_update().execution_options(populate_existing=True)
    return await session.scalar(query)


async def listing(
    session: AsyncSession, owner_id: UUID, limit: int, offset: int, search: str | None = None
) -> list[Project]:
    q = select(Project).where(Project.owner_id == owner_id, Project.deleted_at.is_(None))
    if search:
        escaped = search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        q = q.where(Project.name.ilike(f"%{escaped}%", escape="\\"))
    return list(
        (
            await session.scalars(
                q.order_by(Project.created_at.desc(), Project.id).limit(limit).offset(offset)
            )
        ).all()
    )
