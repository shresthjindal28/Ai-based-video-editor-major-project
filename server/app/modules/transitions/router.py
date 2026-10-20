from fastapi import APIRouter

from app.modules.transitions.service import list_transitions

router = APIRouter(prefix="/transitions", tags=["transitions"])


@router.get("")
async def registry():
    return list_transitions()
