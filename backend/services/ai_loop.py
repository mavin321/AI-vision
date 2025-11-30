import asyncio
import logging
import threading
import time
from collections import deque
from typing import Callable, Deque, Optional

try:
    import cv2
except Exception:
    cv2 = None

from backend.models.gesture_model import GesturePrediction
from backend.models.mapping_model import GestureMapping, MappingConfig
from backend.services.keyboard_service import KeyboardService
from backend.services.vision_service import VisionService

logger = logging.getLogger(__name__)


class GestureState:
    def __init__(self) -> None:
        self.latest: Optional[GesturePrediction] = None
        self.enabled: bool = True
        self.last_frame_jpeg: Optional[bytes] = None

    def update(self, prediction: GesturePrediction) -> None:
        self.latest = prediction

    def toggle(self, enabled: bool) -> None:
        self.enabled = enabled

    def update_frame(self, frame) -> None:
        """Store latest frame as JPEG bytes for preview."""
        if cv2 is None or frame is None:
            return
        ok, encoded = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
        if ok:
            self.last_frame_jpeg = encoded.tobytes()


class GestureBroadcaster:
    def __init__(self) -> None:
        self._listeners: Deque[Callable[[GesturePrediction], None]] = deque()

    def subscribe(self, fn: Callable[[GesturePrediction], None]) -> None:
        self._listeners.append(fn)

    def emit(self, prediction: GesturePrediction) -> None:
        for listener in list(self._listeners):
            try:
                listener(prediction)
            except Exception as exc:  # pragma: no cover - guard
                logger.warning("Gesture listener failed: %s", exc)


class AILoopService:
    def __init__(
        self,
        vision_service: VisionService,
        keyboard_service: KeyboardService,
        mapping_config: MappingConfig,
        gesture_state: GestureState,
        broadcaster: GestureBroadcaster,
        target_fps: int = 12,
    ) -> None:
        self.vision = vision_service
        self.keyboard = keyboard_service
        self.mapping_config = mapping_config
        self.gesture_state = gesture_state
        self.broadcaster = broadcaster
        self.target_fps = target_fps
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._last_label: Optional[str] = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self.vision.start()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=2)
        self.vision.stop()

    def _run_loop(self) -> None:
        interval = 1.0 / max(self.target_fps, 1)
        while not self._stop_event.is_set():
            start = time.time()
            frame = self.vision.read_frame()
            if frame is None:
                time.sleep(interval)
                continue
            frame = self.vision.preprocess(frame)
            self.gesture_state.update_frame(frame)
            label, conf = self.vision.extract_landmarks(frame)
            prediction = GesturePrediction(label=label, confidence=conf)
            self.gesture_state.update(prediction)
            self.broadcaster.emit(prediction)
            if label != self._last_label:
                logger.info("Gesture changed: %s (%.2f)", label, conf)
                self._last_label = label
            self._apply_mapping(prediction)
            elapsed = time.time() - start
            sleep_time = max(interval - elapsed, 0)
            time.sleep(sleep_time)

    def _apply_mapping(self, prediction: GesturePrediction) -> None:
        if not self.gesture_state.enabled:
            return
        mapping_index = self.mapping_config.to_index()
        mapping: Optional[GestureMapping] = mapping_index.get(prediction.label)
        if not mapping:
            return
        self.keyboard.press_action(mapping)

    def update_mappings(self, config: MappingConfig) -> None:
        self.mapping_config = config

    async def stream_predictions(self):
        q: asyncio.Queue[GesturePrediction] = asyncio.Queue()

        def push(pred: GesturePrediction) -> None:
            try:
                q.put_nowait(pred)
            except asyncio.QueueFull:
                pass

        self.broadcaster.subscribe(push)
        while True:
            yield await q.get()
