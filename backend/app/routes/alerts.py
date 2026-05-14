"""
ARIA Backend — routes/alerts.py
REST API controller for alert endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.alert_schema import AlertCreate
from app.services import alert_service

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


@router.get("", summary="Get all active alerts (prioritized)")
def list_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity: low|medium|high|critical"),
    grouped: Optional[bool] = Query(False, description="Return alerts grouped by zone and severity"),
    db: Session = Depends(get_db),
):
    """
    Returns all active alerts sorted by severity (critical first).
    Optional ?severity=critical or ?grouped=true query params.
    """
    if grouped:
        return alert_service.get_grouped_alerts(db)
    if severity:
        return alert_service.get_alerts_by_severity(severity, db)
    return alert_service.get_all_alerts(db)


@router.post("", summary="Create a new alert", status_code=201)
def create_alert(payload: AlertCreate, db: Session = Depends(get_db)):
    try:
        return alert_service.create_alert(payload, db)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
