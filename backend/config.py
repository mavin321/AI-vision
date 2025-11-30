import os
from pathlib import Path
from typing import Optional

from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Local AI Vision Keyboard"
    model_path: Path = Path(os.getenv("MODEL_PATH", "../models/hand_model.tflite"))
    mappings_path: Path = Path(os.getenv("MAPPINGS_PATH", "./mappings.json"))
    use_cpp_extension: bool = False
    camera_index: int = 0
    ai_loop_fps: int = 24
    enable_keyboard_output: bool = True
    ws_route: str = "/ws/gestures"

    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    return Settings()
