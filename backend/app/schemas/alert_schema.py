"""
ARIA Backend — schemas/alert_schema.py
Pydantic request/response schemas for alerts.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AlertBase(BaseModel):
    sensor_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    severity: str   # low | medium | high | critical
    zone: str
    status: Optional[str] = "active"


class AlertCreate(AlertBase):
    pass


class AlertResponse(AlertBase):
    id: int
    created_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None

    class Config:
        from_attributes = True
