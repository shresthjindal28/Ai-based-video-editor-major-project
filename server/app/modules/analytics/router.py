from fastapi import APIRouter

from app.modules.analytics.service import usage_summary
from app.modules.auth.dependencies import DB, CurrentUser

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/usage")
async def usage(db: DB, user: CurrentUser):
    return await usage_summary(db, user.id)
