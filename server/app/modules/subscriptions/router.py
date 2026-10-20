from fastapi import APIRouter

from app.modules.auth.dependencies import CurrentUser

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/current")
async def current(user: CurrentUser):
    return {"plan": "self_hosted_free", "billing": "not_configured", "account_status": user.status}
