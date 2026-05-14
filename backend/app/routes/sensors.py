"""
ARIA Backend — routes/sensors.py
REST API controller for sensor endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.sensor_schema import SensorCreate
from app.services import sensor_service

router = APIRouter(prefix="/api/sensors", tags=["Sensors"])


@router.get("", summary="Get all sensors")
def list_sensors(
    zone: Optional[str] = Query(None, description="Filter by zone, e.g. 'Zone A'"),
    db: Session = Depends(get_db),
):
    """
    Returns all sensors with their live values and status.
    Automatically falls back to mock data if DB is unavailable.
    """
    if zone:
        return sensor_service.get_sensors_by_zone(zone, db)
    return sensor_service.get_all_sensors(db)


@router.get("/{sensor_id}", summary="Get sensor by ID")
def get_sensor(sensor_id: int, db: Session = Depends(get_db)):
    result = sensor_service.get_sensor_by_id(sensor_id, db)
    if not result:
        raise HTTPException(status_code=404, detail=f"Sensor {sensor_id} not found")
    return result


@router.post("", summary="Create a new sensor", status_code=201)
def create_sensor(payload: SensorCreate, db: Session = Depends(get_db)):
    try:
        return sensor_service.create_sensor(payload, db)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
