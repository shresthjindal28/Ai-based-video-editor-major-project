from uuid import UUID

from fastapi import APIRouter, Response

from app.common.utils.pagination import Limit, Offset
from app.modules.auth.dependencies import DB, CurrentUser
from app.modules.editor.schemas import EditVersionOut
from app.modules.jobs.schemas import JobOut
from app.modules.projects import repository, service
from app.modules.projects.schemas import ProjectCreate, ProjectOut, ProjectUpdate
from app.modules.uploads.schemas import AssetOut

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectOut, status_code=201)
async def create(data: ProjectCreate, db: DB, user: CurrentUser):
    project = await service.create(db, user.id, data)
    await db.commit()
    from app.integrations.redis_client import Cache

    await Cache().invalidate_prefix(f"project-list:{user.id}:")
    return project


@router.get("", response_model=list[ProjectOut])
async def listing(
    db: DB, user: CurrentUser, limit: Limit = 25, offset: Offset = 0, search: str | None = None
):
    if search:
        return await repository.listing(db, user.id, limit, offset, search)
    from app.integrations.redis_client import Cache

    cache = Cache()
    key = cache.key("project-list", str(user.id), f"{limit}:{offset}")
    return await cache.get_or_load(
        key, lambda: _cached_listing(db, user.id, limit, offset), negative_ttl=0
    )


@router.get("/{project_id}/assets", response_model=list[AssetOut])
async def project_assets(
    project_id: UUID, db: DB, user: CurrentUser, limit: Limit = 25, offset: Offset = 0
):
    from app.modules.assets.service import project_assets as list_assets

    return await list_assets(db, project_id, user.id, limit, offset)


@router.get("/{project_id}/edits", response_model=list[EditVersionOut])
async def project_edits(
    project_id: UUID, db: DB, user: CurrentUser, limit: Limit = 25, offset: Offset = 0
):
    from app.modules.editor.repository import listing as list_versions

    await service.require_project(db, project_id, user.id)
    return await list_versions(db, project_id, limit, offset)


@router.get("/{project_id}/jobs", response_model=list[JobOut])
async def project_jobs(
    project_id: UUID, db: DB, user: CurrentUser, limit: Limit = 25, offset: Offset = 0
):
    from sqlalchemy import select

    from app.modules.jobs.models import EditJob

    await service.require_project(db, project_id, user.id)
    rows = await db.scalars(
        select(EditJob)
        .where(EditJob.project_id == project_id)
        .order_by(EditJob.created_at.desc(), EditJob.id)
        .limit(limit)
        .offset(offset)
    )
    return list(rows.all())


@router.get("/{project_id}/exports")
async def project_exports(
    project_id: UUID, db: DB, user: CurrentUser, limit: Limit = 25, offset: Offset = 0
):
    from sqlalchemy import select

    from app.modules.exports.models import RenderOutput

    await service.require_project(db, project_id, user.id)
    rows = await db.scalars(
        select(RenderOutput)
        .where(RenderOutput.project_id == project_id)
        .order_by(RenderOutput.created_at.desc(), RenderOutput.id)
        .limit(limit)
        .offset(offset)
    )
    return list(rows.all())


async def _cached_listing(db, user_id, limit, offset):
    from app.modules.projects.schemas import ProjectOut

    return [
        item.model_dump(mode="json")
        for item in (
            ProjectOut.model_validate(row)
            for row in await repository.listing(db, user_id, limit, offset)
        )
    ]


@router.get("/{project_id}", response_model=ProjectOut)
async def get(project_id: UUID, db: DB, user: CurrentUser):
    return await service.require_project(db, project_id, user.id)


@router.patch("/{project_id}", response_model=ProjectOut)
async def patch(project_id: UUID, data: ProjectUpdate, db: DB, user: CurrentUser):
    project = await service.update(db, project_id, user.id, data)
    await db.commit()
    from app.integrations.redis_client import Cache

    await Cache().invalidate_prefix(f"project-list:{user.id}:")
    await Cache().invalidate(f"project-detail:{user.id}:{project_id}")
    return project


@router.delete("/{project_id}", status_code=204)
async def delete(project_id: UUID, db: DB, user: CurrentUser):
    await service.delete(db, project_id, user.id)
    await db.commit()
    from app.integrations.redis_client import Cache

    await Cache().invalidate_prefix(f"project-list:{user.id}:")
    await Cache().invalidate(f"project-detail:{user.id}:{project_id}")
    return Response(status_code=204)
