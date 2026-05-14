"""
ARIA Backend — schemas/sensor_schema.py
Pydantic request/response schemas for sensors.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class SensorBase(BaseModel):
    name: str
    zone: str
    type: str
    unit: str
    value: float
    min_threshold: float
    max_threshold: float
    status: Optional[str] = "normal"


class SensorCreate(SensorBase):
    pass


class SensorResponse(SensorBase):
    id: int
    last_updated: Optional[datetime] = None

    class Config:
        from_attributes = True


class SensorHistoryResponse(BaseModel):
    id: int
    sensor_id: int
    value: float
    recorded_at: Optional[datetime] = None

    class Config:
        from_attributes = True
