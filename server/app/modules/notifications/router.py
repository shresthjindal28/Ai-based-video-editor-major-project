from fastapi import APIRouter

from app.common.utils.pagination import Limit, Offset
from app.modules.auth.dependencies import DB, CurrentUser
from app.modules.notifications.repository import list_for_user
from app.modules.notifications.schemas import NotificationOut

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationOut])
async def listing(db: DB, user: CurrentUser, limit: Limit = 25, offset: Offset = 0):
    return await list_for_user(db, user.id, limit, offset)
