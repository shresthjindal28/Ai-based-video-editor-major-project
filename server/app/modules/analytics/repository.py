from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.assets.models import MediaAsset
from app.modules.exports.models import RenderOutput
from app.modules.jobs.models import EditJob
from app.modules.projects.models import Project


async def usage(session: AsyncSession, user_id: UUID) -> dict[str, int]:
    projects = await session.scalar(
        select(func.count(Project.id)).where(
            Project.owner_id == user_id, Project.deleted_at.is_(None)
        )
    )
    assets = await session.scalar(
        select(func.count(MediaAsset.id)).where(
            MediaAsset.owner_id == user_id, MediaAsset.deleted_at.is_(None)
        )
    )
    storage_bytes = await session.scalar(
        select(func.coalesce(func.sum(MediaAsset.file_size), 0)).where(
            MediaAsset.owner_id == user_id, MediaAsset.deleted_at.is_(None)
        )
    )
    jobs = await session.scalar(
        select(func.count(EditJob.id))
        .join(Project, Project.id == EditJob.project_id)
        .where(Project.owner_id == user_id)
    )
    renders = await session.scalar(
        select(func.count(RenderOutput.id))
        .join(Project, Project.id == RenderOutput.project_id)
        .where(Project.owner_id == user_id)
    )
    return {
        "projects": projects or 0,
        "assets": assets or 0,
        "jobs": jobs or 0,
        "renders": renders or 0,
        "storage_bytes": storage_bytes or 0,
    }
