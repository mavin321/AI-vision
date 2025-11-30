from fastapi import APIRouter, Depends, Request

from backend.models.mapping_model import ActionType, GestureMapping, MappingConfig
from backend.services.ai_loop import AILoopService
from backend.services.keyboard_service import KeyboardService

router = APIRouter(prefix="/api/keyboard", tags=["keyboard"])


def get_keyboard(request: Request) -> KeyboardService:
    return request.app.state.keyboard  # type: ignore[attr-defined]


def get_loop(request: Request) -> AILoopService:
    return request.app.state.ai_loop  # type: ignore[attr-defined]


@router.post("/press")
async def press_key(mapping: GestureMapping, keyboard: KeyboardService = Depends(get_keyboard)) -> dict:
    keyboard.press_action(mapping)
    return {"status": "ok"}
