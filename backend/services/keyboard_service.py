import logging
import time
from typing import Iterable, List

from backend.models.mapping_model import ActionType, GestureMapping

logger = logging.getLogger(__name__)


class KeyboardService:
    def __init__(self, enabled: bool = True) -> None:
        self.enabled = enabled
        self._controller = None
        self._keyboard_lib = None
        self._load_backend()

    def _load_backend(self) -> None:
        try:
            from pynput.keyboard import Controller, Key

            self._controller = Controller()
            self._keyboard_lib = Key
            logger.info("Loaded pynput for keyboard control")
        except Exception:  # pragma: no cover - fallback path
            try:
                import keyboard as kb

                self._controller = kb
                self._keyboard_lib = kb
                logger.info("Loaded keyboard library fallback")
            except Exception as exc:  # pragma: no cover
                logger.warning("Keyboard control unavailable: %s", exc)
                self.enabled = False

    def press_action(self, mapping: GestureMapping) -> None:
        if not self.enabled or not self._controller:
            logger.debug("Keyboard output disabled or unavailable")
            return

        if mapping.action_type == ActionType.key:
            self._press_key(mapping.action)
        elif mapping.action_type == ActionType.shortcut:
            sequence = [part.strip() for part in mapping.action.split("+") if part.strip()]
            self._press_combo(sequence)
        elif mapping.action_type == ActionType.macro:
            sequence = [part.strip() for part in mapping.action.split(",") if part.strip()]
            for key in sequence:
                self._press_key(key, hold_ms=mapping.hold_ms)
        else:  # pragma: no cover - future proof
            logger.warning("Unknown action type: %s", mapping.action_type)

    def _press_key(self, key: str, hold_ms: int = 50) -> None:
        try:
            if hasattr(self._controller, "press") and hasattr(self._controller, "release"):
                self._controller.press(key)
                time.sleep(max(hold_ms / 1000.0, 0))
                self._controller.release(key)
            else:
                # keyboard lib
                self._controller.send(key)
        except Exception as exc:  # pragma: no cover - hardware specific
            logger.error("Failed to press key %s: %s", key, exc)

    def _press_combo(self, keys: Iterable[str]) -> None:
        keys_list: List[str] = list(keys)
        logger.debug("Pressing combo: %s", "+".join(keys_list))
        try:
            if hasattr(self._controller, "press"):
                for key in keys_list:
                    self._controller.press(key)
                for key in reversed(keys_list):
                    self._controller.release(key)
            else:
                self._controller.send("+".join(keys_list))
        except Exception as exc:  # pragma: no cover
            logger.error("Failed to press combo %s: %s", keys_list, exc)
