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
        if self.camera_index < 0:
            logger.info("Camera index < 0; skipping capture start")
            return
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            logger.error("Unable to open camera %s", self.camera_index)
            self.cap = None
            return
        if mp is not None:
            self._mp_hands = mp.solutions.hands.Hands(
                static_image_mode=False,
                max_num_hands=1,
                min_detection_confidence=0.3,
                min_tracking_confidence=0.3,
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
        # MediaPipe prefers near-original frames; use light blur to reduce noise.
        if mp is not None and cv2 is not None:
            return cv2.GaussianBlur(frame, (5, 5), 0)
        if self.use_cpp_extension:
            try:
                return vision.preprocess(frame)
            except Exception as exc:  # pragma: no cover - extension runtime guard
                logger.warning("C++ extension failed, falling back to numpy/cv: %s", exc)
        if cv2 is None:
            return frame
        return cv2.GaussianBlur(frame, (5, 5), 0)

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
        landmarks = result.multi_hand_landmarks[0]

        # Landmark aliases
        wrist = landmarks.landmark[0]
        thumb_tip = landmarks.landmark[4]
        index_tip = landmarks.landmark[8]
        middle_tip = landmarks.landmark[12]
        ring_tip = landmarks.landmark[16]
        pinky_tip = landmarks.landmark[20]

        def finger_extended(tip, base_idx: int) -> bool:
            base = landmarks.landmark[base_idx]
            return tip.y < base.y - 0.02

        pinch_dist = abs(thumb_tip.x - index_tip.x) + abs(thumb_tip.y - index_tip.y)
        thumb_up = thumb_tip.y < wrist.y - 0.05
        thumb_down = thumb_tip.y > wrist.y + 0.08

        index_ext = finger_extended(index_tip, 5)
        middle_ext = finger_extended(middle_tip, 9)
        ring_ext = finger_extended(ring_tip, 13)
        pinky_ext = finger_extended(pinky_tip, 17)

        extended_count = sum([index_ext, middle_ext, ring_ext, pinky_ext])

        # Heuristic ordering
        if pinch_dist < 0.1 and index_ext:
            return "pinch", 0.85
        if thumb_up and not index_ext and not middle_ext:
            return "thumbs_up", 0.75
        if thumb_down and not index_ext and not middle_ext:
            return "thumbs_down", 0.75
        if index_ext and not middle_ext and not ring_ext and not pinky_ext:
            return "point", 0.7
        if extended_count <= 1 and pinch_dist >= 0.1:
            return "fist", 0.65
        if extended_count >= 3:
            return "open_hand", 0.65
        return "unknown", 0.4
