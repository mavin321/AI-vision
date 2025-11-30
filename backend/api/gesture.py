from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response

from backend.models.gesture_model import GestureStatus, GestureToggle
from backend.services.ai_loop import AILoopService, GestureState

router = APIRouter(prefix="/api/gesture", tags=["gesture"])


def get_state(request: Request) -> GestureState:
    state: GestureState = request.app.state.gesture_state  # type: ignore[attr-defined]
    return state


def get_loop(request: Request) -> AILoopService:
    loop: AILoopService = request.app.state.ai_loop  # type: ignore[attr-defined]
    return loop


@router.get("", response_model=GestureStatus)
async def read_gesture(state: GestureState = Depends(get_state)) -> GestureStatus:
    return GestureStatus(latest=state.latest, enabled=state.enabled)


@router.post("", response_model=GestureStatus)
async def toggle_gesture(
    payload: GestureToggle,
    state: GestureState = Depends(get_state),
    loop: AILoopService = Depends(get_loop),
) -> GestureStatus:
    state.toggle(payload.enabled)
    if payload.enabled:
        loop.start()
    else:
        loop.stop()
    return GestureStatus(latest=state.latest, enabled=state.enabled)


@router.get("/frame")
async def preview_frame(state: GestureState = Depends(get_state)) -> Response:
    if state.last_frame_jpeg is None:
        return Response(status_code=204)
    return Response(content=state.last_frame_jpeg, media_type="image/jpeg")
