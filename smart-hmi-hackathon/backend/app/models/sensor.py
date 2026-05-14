"""
ARIA Backend — models/sensor.py
SQLAlchemy ORM model for the sensors and sensor_history tables.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, func
from app.database import Base


class Sensor(Base):
    __tablename__ = "sensors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    zone = Column(String(50), nullable=False)
    type = Column(String(50), nullable=False)       # temperature | pressure | flow | vibration
    unit = Column(String(20), nullable=False)
    value = Column(Float, nullable=False)
    min_threshold = Column(Float, nullable=False)
    max_threshold = Column(Float, nullable=False)
    status = Column(String(20), default="normal")   # normal | warning | critical
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())


class SensorHistory(Base):
    __tablename__ = "sensor_history"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, nullable=False)
    value = Column(Float, nullable=False)
    recorded_at = Column(DateTime, default=func.now())
