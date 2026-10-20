from dataclasses import asdict
from uuid import UUID

from fastapi import APIRouter
from sqlalchemy import select

from app.modules.assets.models import MediaAsset
from app.modules.auth.dependencies import DB, CurrentUser
from app.modules.editor.compiler import compile_plan
from app.modules.editor.schemas import TimelinePlan
from app.modules.editor.service import get_version

router = APIRouter(tags=["timelines"])


@router.get("/projects/{project_id}/edits/{version_id}/timeline")
async def inspect(project_id: UUID, version_id: UUID, db: DB, user: CurrentUser):
    version = await get_version(db, project_id, user.id, version_id)
    plan = TimelinePlan.model_validate(version.timeline)
    identities = {clip.asset_id for clip in plan.clips} | {audio.asset_id for audio in plan.audio}
    sources = list((await db.scalars(select(MediaAsset).where(MediaAsset.project_id == project_id,
                 MediaAsset.owner_id == user.id, MediaAsset.id.in_(identities)))).all())
    rates = {asset.id: (asset.fps_num or plan.output.fps_num, asset.fps_den or plan.output.fps_den) for asset in sources}
    return {"version_id": version.id, "timeline": plan.model_dump(mode="json"),
            "compiled": asdict(compile_plan(plan, rates))}
