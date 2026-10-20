from uuid import UUID

from fastapi import APIRouter, Header

from app.common.utils.pagination import Limit, Offset
from app.modules.auth.dependencies import DB, CurrentUser
from app.modules.auth.idempotency import begin, finish
from app.modules.editor import repository, service
from app.modules.editor.schemas import EditVersionOut, TimelinePlan

router = APIRouter(prefix="/projects/{project_id}/edits", tags=["editing"])


@router.post("/validate", status_code=200)
async def validate(project_id: UUID, plan: TimelinePlan, db: DB, user: CurrentUser):
    await service.validate(db, project_id, user.id, plan)
    return {"valid": True, "schema_version": plan.schema_version}


@router.post("", response_model=EditVersionOut, status_code=201)
async def create(
    project_id: UUID,
    plan: TimelinePlan,
    db: DB,
    user: CurrentUser,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    record = await begin(
        db, user.id, f"edit-version:{project_id}", idempotency_key, plan.model_dump(mode="json")
    )
    if record and record.status == "completed" and record.result:
        return await service.get_version(db, project_id, user.id, UUID(record.result["version_id"]))
    version = await service.create_version(db, project_id, user.id, plan)
    finish(record, {"version_id": str(version.id)})
    await db.commit()
    return version


@router.get("", response_model=list[EditVersionOut])
async def listing(
    project_id: UUID, db: DB, user: CurrentUser, limit: Limit = 25, offset: Offset = 0
):
    from app.modules.projects.service import require_project

    await require_project(db, project_id, user.id)
    return await repository.listing(db, project_id, limit, offset)


@router.get("/{version_id}", response_model=EditVersionOut)
async def get(project_id: UUID, version_id: UUID, db: DB, user: CurrentUser):
    return await service.get_version(db, project_id, user.id, version_id)


@router.post("/{version_id}/revisions", response_model=EditVersionOut, status_code=201)
async def revise(
    project_id: UUID,
    version_id: UUID,
    plan: TimelinePlan,
    db: DB,
    user: CurrentUser,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
):
    record = await begin(
        db,
        user.id,
        f"edit-revision:{version_id}",
        idempotency_key,
        {"parent": str(version_id), "plan": plan.model_dump(mode="json")},
    )
    if record and record.status == "completed" and record.result:
        return await service.get_version(db, project_id, user.id, UUID(record.result["version_id"]))
    version = await service.create_version(db, project_id, user.id, plan, parent_id=version_id)
    finish(record, {"version_id": str(version.id)})
    await db.commit()
    return version
