from fastapi import APIRouter

from app.modules.effects.service import list_effects

router = APIRouter(prefix="/effects", tags=["effects"])


@router.get("")
async def registry():
    return list_effects()
