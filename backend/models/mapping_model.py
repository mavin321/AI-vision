from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ActionType(str, Enum):
    key = "key"
    shortcut = "shortcut"
    macro = "macro"


class GestureMapping(BaseModel):
    gesture: str = Field(..., description="Gesture label")
    action: str = Field(..., description="Key or macro to trigger")
    action_type: ActionType = ActionType.key
    hold_ms: int = Field(50, description="How long to hold the key in milliseconds")


class MappingConfig(BaseModel):
    mappings: List[GestureMapping] = Field(default_factory=list)

    def to_index(self) -> Dict[str, GestureMapping]:
        return {m.gesture: m for m in self.mappings}
