import asyncio
import logging
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend.api import gesture, keyboard, mappings
from backend.config import Settings, get_settings
from backend.models.gesture_model import GesturePrediction
from backend.models.mapping_model import GestureMapping, MappingConfig
from backend.services.ai_loop import AILoopService, GestureBroadcaster, GestureState
from backend.services.keyboard_service import KeyboardService
from backend.services.vision_service import VisionService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Local AI Vision Keyboard")
app.include_router(gesture.router)
app.include_router(mappings.router)
app.include_router(keyboard.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.on_event("startup")
async def startup_event() -> None:
    settings: Settings = get_settings()
    mappings_path: Path = settings.mappings_path
    if mappings_path.exists():
        mapping_config = MappingConfig.parse_raw(mappings_path.read_text())
    else:
        default = MappingConfig(
            mappings=[
                GestureMapping(gesture="open_hand", action="space", action_type="key"),
                GestureMapping(gesture="pinch", action="ctrl+c", action_type="shortcut"),
            ]
        )
        mappings_path.write_text(default.json(indent=2))
        mapping_config = default

    gesture_state = GestureState()
    broadcaster = GestureBroadcaster()
    vision_service = VisionService(
        camera_index=settings.camera_index, use_cpp_extension=settings.use_cpp_extension
    )
    keyboard_service = KeyboardService(enabled=settings.enable_keyboard_output)
    ai_loop = AILoopService(
        vision_service=vision_service,
        keyboard_service=keyboard_service,
        mapping_config=mapping_config,
        gesture_state=gesture_state,
        broadcaster=broadcaster,
        target_fps=settings.ai_loop_fps,
    )
    # Start only if camera index is valid
    if settings.camera_index >= 0:
        ai_loop.start()

    app.state.settings = settings
    app.state.mapping_config = mapping_config
    app.state.ai_loop = ai_loop
    app.state.gesture_state = gesture_state
    app.state.broadcaster = broadcaster
    app.state.keyboard = keyboard_service
    app.state.mappings_path = mappings_path


@app.on_event("shutdown")
async def shutdown_event() -> None:
    if hasattr(app.state, "ai_loop"):
        app.state.ai_loop.stop()


@app.websocket("/ws/gestures")
async def gesture_stream(websocket: WebSocket):
    await websocket.accept()
    broadcaster: GestureBroadcaster = app.state.broadcaster  # type: ignore[attr-defined]
    queue: asyncio.Queue[GesturePrediction] = asyncio.Queue()

    def push(pred: GesturePrediction) -> None:
        try:
            queue.put_nowait(pred)
        except asyncio.QueueFull:
            pass

    broadcaster.subscribe(push)

    try:
        while True:
            prediction = await queue.get()
            await websocket.send_json(
                {
                    "label": prediction.label,
                    "confidence": prediction.confidence,
                    "timestamp": prediction.timestamp.isoformat(),
                }
            )
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected")
    finally:
        # nothing to clean up because listeners are weak
        ...


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}


# Entry point for manual runs
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=False)
