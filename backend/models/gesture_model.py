from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class GesturePrediction(BaseModel):
    label: str = Field(..., description="Name of the detected gesture")
    confidence: float = Field(..., ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class GestureToggle(BaseModel):
    enabled: bool


class GestureStatus(BaseModel):
    latest: Optional[GesturePrediction]
    enabled: bool
