"""
ARIA Backend — services/sensor_service.py
Business logic for sensors.
Implements DB-first with automatic mock data fallback.
"""

from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.models.sensor import Sensor, SensorHistory
from app.schemas.sensor_schema import SensorCreate


# ─────────────────────────────────────────────
#  MOCK DATA (used when DB is unavailable/empty)
# ─────────────────────────────────────────────
MOCK_SENSORS: List[Dict[str, Any]] = [
    {"id": 1, "name": "Pump 1 Temp",     "zone": "Zone A", "type": "temperature", "unit": "C",     "value": 72.5, "min_threshold": 0.0,  "max_threshold": 80.0,  "status": "warning",  "last_updated": "2026-05-14T12:00:00"},
    {"id": 2, "name": "Pump 2 Temp",     "zone": "Zone A", "type": "temperature", "unit": "C",     "value": 45.0, "min_threshold": 0.0,  "max_threshold": 80.0,  "status": "normal",   "last_updated": "2026-05-14T12:00:00"},
    {"id": 3, "name": "Pump 3 Temp",     "zone": "Zone B", "type": "temperature", "unit": "C",     "value": 88.0, "min_threshold": 0.0,  "max_threshold": 80.0,  "status": "critical", "last_updated": "2026-05-14T12:00:00"},
    {"id": 4, "name": "Valve 1 Press",   "zone": "Zone A", "type": "pressure",    "unit": "bar",   "value": 4.2,  "min_threshold": 1.0,  "max_threshold": 5.0,   "status": "normal",   "last_updated": "2026-05-14T12:00:00"},
    {"id": 5, "name": "Valve 4 Press",   "zone": "Zone B", "type": "pressure",    "unit": "bar",   "value": 4.9,  "min_threshold": 1.0,  "max_threshold": 5.0,   "status": "warning",  "last_updated": "2026-05-14T12:00:00"},
    {"id": 6, "name": "Coolant Flow",    "zone": "Zone C", "type": "flow",        "unit": "L/min", "value": 120.0,"min_threshold": 80.0, "max_threshold": 200.0, "status": "normal",   "last_updated": "2026-05-14T12:00:00"},
    {"id": 7, "name": "Motor Vibration", "zone": "Zone B", "type": "vibration",   "unit": "mm/s",  "value": 6.8,  "min_threshold": 0.0,  "max_threshold": 5.0,   "status": "critical", "last_updated": "2026-05-14T12:00:00"},
    {"id": 8, "name": "Pipe Pressure",   "zone": "Zone C", "type": "pressure",    "unit": "bar",   "value": 3.1,  "min_threshold": 1.0,  "max_threshold": 5.0,   "status": "normal",   "last_updated": "2026-05-14T12:00:00"},
]


def _sensor_to_dict(sensor: Sensor) -> Dict[str, Any]:
    return {
        "id": sensor.id,
        "name": sensor.name,
        "zone": sensor.zone,
        "type": sensor.type,
        "unit": sensor.unit,
        "value": sensor.value,
        "min_threshold": sensor.min_threshold,
        "max_threshold": sensor.max_threshold,
        "status": sensor.status,
        "last_updated": sensor.last_updated.isoformat() if sensor.last_updated else None,
    }


# ─────────────────────────────────────────────
#  SERVICE FUNCTIONS
# ─────────────────────────────────────────────

def get_all_sensors(db: Session) -> Dict[str, Any]:
    """
    Try DB first. Fall back to mock data if DB is empty or unreachable.
    Always returns identical JSON shape.
    """
    try:
        sensors = db.query(Sensor).all()
        if sensors:
            return {
                "data_source": "database",
                "count": len(sensors),
                "sensors": [_sensor_to_dict(s) for s in sensors],
            }
    except Exception:
        pass

    return {
        "data_source": "mock",
        "count": len(MOCK_SENSORS),
        "sensors": MOCK_SENSORS,
    }


def get_sensor_by_id(sensor_id: int, db: Session) -> Dict[str, Any] | None:
    try:
        sensor = db.query(Sensor).filter(Sensor.id == sensor_id).first()
        if sensor:
            return {"data_source": "database", "sensor": _sensor_to_dict(sensor)}
    except Exception:
        pass

    # Look in mock data
    mock = next((s for s in MOCK_SENSORS if s["id"] == sensor_id), None)
    if mock:
        return {"data_source": "mock", "sensor": mock}
    return None


def create_sensor(payload: SensorCreate, db: Session) -> Dict[str, Any]:
    try:
        sensor = Sensor(**payload.model_dump())
        db.add(sensor)
        db.commit()
        db.refresh(sensor)
        return {"data_source": "database", "sensor": _sensor_to_dict(sensor)}
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"DB write failed: {e}")


def get_sensors_by_zone(zone: str, db: Session) -> Dict[str, Any]:
    try:
        sensors = db.query(Sensor).filter(Sensor.zone == zone).all()
        if sensors:
            return {
                "data_source": "database",
                "zone": zone,
                "sensors": [_sensor_to_dict(s) for s in sensors],
            }
    except Exception:
        pass

    mock = [s for s in MOCK_SENSORS if s["zone"] == zone]
    return {"data_source": "mock", "zone": zone, "sensors": mock}
