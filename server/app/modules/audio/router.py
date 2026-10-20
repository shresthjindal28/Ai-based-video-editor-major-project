from uuid import UUID

from fastapi import APIRouter
from sqlalchemy import select

from app.common.utils.pagination import Limit, Offset
from app.modules.assets.models import MediaAsset
from app.modules.auth.dependencies import DB, CurrentUser
from app.modules.projects.service import require_project
from app.modules.uploads.schemas import AssetOut

router = APIRouter(tags=["audio"])


@router.get("/audio/capabilities")
async def capabilities():
    return {"tracks_max":16, "gain":{"minimum":0,"maximum":4}, "fades":"linear, integer output frames",
            "volume_keyframes":"clip-relative integer frames, linear gain", "sample_rate":48000,
            "channels":2, "mixing":"MLT additive source/music mixing; source gain defaults to 1"}


@router.get("/projects/{project_id}/audio", response_model=list[AssetOut])
async def list_audio(project_id: UUID, db: DB, user: CurrentUser, limit: Limit = 25, offset: Offset = 0):
    await require_project(db,project_id,user.id)
    rows=await db.scalars(select(MediaAsset).where(MediaAsset.project_id==project_id,
        MediaAsset.owner_id==user.id,MediaAsset.deleted_at.is_(None),MediaAsset.has_audio.is_(True))
        .order_by(MediaAsset.created_at.desc(),MediaAsset.id).limit(limit).offset(offset))
    return list(rows.all())
