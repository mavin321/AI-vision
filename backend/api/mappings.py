from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request

from backend.models.mapping_model import GestureMapping, MappingConfig
from backend.services.ai_loop import AILoopService

router = APIRouter(prefix="/api/settings", tags=["settings"])


def get_paths(request: Request) -> Path:
    return Path(request.app.state.mappings_path)  # type: ignore[attr-defined]


def get_loop(request: Request) -> AILoopService:
    return request.app.state.ai_loop  # type: ignore[attr-defined]


def get_config(request: Request) -> MappingConfig:
    return request.app.state.mapping_config  # type: ignore[attr-defined]


def _save_config(path: Path, config: MappingConfig) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(config.json(indent=2))


@router.get("", response_model=MappingConfig)
async def read_mappings(config: MappingConfig = Depends(get_config)) -> MappingConfig:
    return config


@router.post("", response_model=MappingConfig)
async def update_mappings(
    payload: MappingConfig,
    path: Path = Depends(get_paths),
    loop: AILoopService = Depends(get_loop),
    request: Request = None,
) -> MappingConfig:
    _save_config(path, payload)
    loop.update_mappings(payload)
    request.app.state.mapping_config = payload  # type: ignore[attr-defined]
    return payload
