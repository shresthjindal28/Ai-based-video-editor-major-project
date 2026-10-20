from fastapi import APIRouter

from app.core.config import get_settings
from app.modules.analytics.service import usage_summary
from app.modules.auth.dependencies import DB, CurrentUser

router = APIRouter(prefix="/usage", tags=["usage limits"])


@router.get("/entitlements")
async def entitlements(db: DB, user: CurrentUser):
    usage = await usage_summary(db, user.id)
    settings = get_settings()
    return {
        "plan": "self_hosted_free",
        "limits": {
            "projects": settings.max_projects_per_user,
            "storage_bytes": settings.max_storage_bytes,
            "upload_bytes": settings.max_upload_size_mb * 1024**2,
            "render_seconds": settings.max_project_duration_seconds,
            "render_seconds_per_month": settings.max_render_seconds_per_month,
            "concurrent_renders": settings.max_concurrent_renders,
        },
        "usage": usage,
    }
