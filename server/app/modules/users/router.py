from fastapi import APIRouter

from app.modules.auth.dependencies import CurrentUser
from app.modules.users.schemas import UserOut

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
async def me(user: CurrentUser):
    from app.modules.users.service import profile

    return profile(user)
