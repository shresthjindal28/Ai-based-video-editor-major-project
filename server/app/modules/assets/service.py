from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.assets.repository import listing
from app.modules.uploads.service import delete_asset


async def delete_owned_asset(session: AsyncSession, asset_id: UUID, owner_id: UUID) -> None:
    await delete_asset(session, asset_id, owner_id)


async def project_assets(
    session: AsyncSession, project_id: UUID, owner_id: UUID, limit: int, offset: int
):
    from app.modules.projects.service import require_project

    await require_project(session, project_id, owner_id)
    return await listing(session, project_id, owner_id, limit, offset)
