"""
ARIA Backend — models/alert.py
SQLAlchemy ORM model for the alerts table.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, nullable=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(20), nullable=False)   # low | medium | high | critical
    zone = Column(String(50), nullable=False)
    status = Column(String(20), default="active")   # active | acknowledged | resolved
    created_at = Column(DateTime, default=func.now())
    resolved_at = Column(DateTime, nullable=True)
