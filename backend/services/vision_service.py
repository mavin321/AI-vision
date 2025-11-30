import logging
from typing import Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

try:
    import cv2
except Exception as exc:  # pragma: no cover - dependency guard
    cv2 = None
    logger.warning("OpenCV not available: %s", exc)

try:
    import mediapipe as mp  # type: ignore
except Exception:
    mp = None

try:
    import vision  # type: ignore  # compiled extension stub
except Exception:
    vision = None


class VisionService:
    def __init__(self, camera_index: int = 0, use_cpp_extension: bool = True) -> None:
        self.camera_index = camera_index
        self.use_cpp_extension = use_cpp_extension and vision is not None
        self.cap = None
        self._mp_hands = None

    def start(self) -> None:
        if cv2 is None:
            logger.error("OpenCV is required to start the camera")
            return
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            logger.error("Unable to open camera %s", self.camera_index)
            self.cap = None
        if mp is not None:
            self._mp_hands = mp.solutions.hands.Hands(
                static_image_mode=False, max_num_hands=1
            )

    def stop(self) -> None:
        if self.cap:
            self.cap.release()
            self.cap = None
        if self._mp_hands:
            self._mp_hands.close()
            self._mp_hands = None

    def read_frame(self) -> Optional[np.ndarray]:
        if not self.cap:
            return None
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def preprocess(self, frame: np.ndarray) -> np.ndarray:
        if self.use_cpp_extension:
            try:
                return vision.preprocess(frame)
            except Exception as exc:  # pragma: no cover - extension runtime guard
                logger.warning("C++ extension failed, falling back to numpy/cv: %s", exc)
        if cv2 is None:
            return frame
        blurred = cv2.GaussianBlur(frame, (5, 5), 0)
        return blurred

    def extract_landmarks(self, frame: np.ndarray) -> Tuple[str, float]:
        """Return gesture label and confidence.

        Uses MediaPipe if available, otherwise returns a dummy prediction.
        """
        if mp is None or cv2 is None or self._mp_hands is None:
            return "unknown", 0.0
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self._mp_hands.process(frame_rgb)
        if not result.multi_hand_landmarks:
            return "unknown", 0.0
        # Basic heuristic: use landmark positions to classify open/closed
        landmarks = result.multi_hand_landmarks[0]
        thumb_tip = landmarks.landmark[4]
        index_tip = landmarks.landmark[8]
        distance = abs(thumb_tip.x - index_tip.x) + abs(thumb_tip.y - index_tip.y)
        if distance < 0.08:
            return "pinch", 0.65
        elif thumb_tip.y < index_tip.y:
            return "thumbs_up", 0.6
        return "open_hand", 0.55
