from uuid import UUID

from fastapi import APIRouter, Request, Response

from app.common.utils.file_download import ranged_file_response
from app.common.utils.pagination import Limit, Offset
from app.core.exceptions import DomainError
from app.integrations.storage_client import storage
from app.modules.assets import service
from app.modules.auth.dependencies import DB, CurrentUser
from app.modules.uploads.schemas import AssetOut
from app.modules.uploads.service import owned_asset

router = APIRouter(prefix="/projects/{project_id}/assets", tags=["assets"])


@router.get("", response_model=list[AssetOut])
async def listing(
    project_id: UUID, db: DB, user: CurrentUser, limit: Limit = 25, offset: Offset = 0
):
    return await service.project_assets(db, project_id, user.id, limit, offset)


@router.get("/{asset_id}", response_model=AssetOut)
async def get(project_id: UUID, asset_id: UUID, db: DB, user: CurrentUser):
    asset = await owned_asset(db, asset_id, user.id)
    if asset.project_id != project_id:
        raise DomainError("asset_not_found", "Asset not found", 404)
    return asset


@router.get("/{asset_id}/download")
async def download(project_id: UUID, asset_id: UUID, request: Request, db: DB, user: CurrentUser):
    asset = await get(project_id, asset_id, db, user)
    path = await storage.materialize(asset.storage_key)
    if not path.is_file():
        raise DomainError("asset_missing", "Stored media is unavailable", 410)
    return ranged_file_response(path, request, asset.mime_type, asset.original_filename)


@router.delete("/{asset_id}", status_code=204)
async def delete(project_id: UUID, asset_id: UUID, db: DB, user: CurrentUser):
    asset = await get(project_id, asset_id, db, user)
    await service.delete_owned_asset(db, asset.id, user.id)
    await db.commit()
    await storage.remove(asset.storage_key)
    return Response(status_code=204)
