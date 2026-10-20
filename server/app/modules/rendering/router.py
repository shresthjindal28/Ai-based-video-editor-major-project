from uuid import UUID

from fastapi import APIRouter, Header

from app.common.middleware.rate_limit import check_expensive_operation
from app.core.exceptions import DomainError
from app.modules.auth.dependencies import DB, CurrentUser
from app.modules.auth.idempotency import begin, finish
from app.modules.editor.service import get_version
from app.modules.jobs.schemas import JobOut
from app.modules.jobs.service import create_render
from app.modules.rendering.schemas import RenderRequest

router = APIRouter(tags=["rendering"])
PRESETS = [
    {"id": "preview", "width": 640, "height": 360, "fps": 24, "quality": "low"},
    {"id": "1080p_landscape", "width": 1920, "height": 1080, "fps": 30, "quality": "high"},
    {"id": "1080p_portrait", "width": 1080, "height": 1920, "fps": 30, "quality": "high"},
    {"id": "1080p_square", "width": 1080, "height": 1080, "fps": 30, "quality": "high"},
]


@router.get("/render-presets")
async def presets():
    return PRESETS


async def _request(
    project_id: UUID,
    version_id: UUID,
    kind: str,
    data: RenderRequest,
    db: DB,
    user: CurrentUser,
    idempotency_key: str | None,
):
    version = await get_version(db, project_id, user.id, version_id)
    await check_expensive_operation(kind, user.id)
    scope = f"render:{version_id}:{kind}"
    record = await begin(db, user.id, scope, idempotency_key, data.model_dump())
    if record and record.status == "completed" and record.result:
        from app.modules.jobs.service import require_job

        return await require_job(db, UUID(record.result["job_id"]), user.id)
    job = await create_render(db, project_id, version.id, user.id, kind, data.preset)
    finish(record, {"job_id": str(job.id)})
    await db.commit()
    return job


@router.post(
    "/projects/{project_id}/edits/{version_id}/preview", response_model=JobOut, status_code=202
)
async def preview(
    project_id: UUID,
    version_id: UUID,
    data: RenderRequest,
    db: DB,
    user: CurrentUser,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    if data.preset != "preview":
        raise DomainError(
            "invalid_preview_preset", "Preview requests must use the preview preset", 422
        )
    return await _request(project_id, version_id, "preview", data, db, user, idempotency_key)


@router.post(
    "/projects/{project_id}/edits/{version_id}/render", response_model=JobOut, status_code=202
)
async def render(
    project_id: UUID,
    version_id: UUID,
    data: RenderRequest,
    db: DB,
    user: CurrentUser,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    return await _request(project_id, version_id, "render", data, db, user, idempotency_key)
