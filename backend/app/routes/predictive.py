"""
ARIA Backend — routes/predictive.py
REST API controller for predictive analytics and AI suggestions.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import ai_service

router = APIRouter(tags=["AI & Predictive"])


@router.get("/api/predictive-alerts", summary="Get AI-generated predictive alerts")
def predictive_alerts(db: Session = Depends(get_db)):
    """
    Analyses sensor values against thresholds.
    Returns time-to-breach predictions for sensors approaching limits.
    """
    return ai_service.get_predictive_alerts(db)


@router.get("/api/ai-suggestions", summary="Get AI-generated action suggestions")
def ai_suggestions(db: Session = Depends(get_db)):
    """
    Rule-based AI suggestions derived from sensor status and alert severity.
    Example: 'Check Valve 4 immediately — pressure near max.'
    """
    return ai_service.get_ai_suggestions(db)


@router.get("/api/dashboard-summary", summary="Get plant-wide dashboard summary")
def dashboard_summary(db: Session = Depends(get_db)):
    """
    Returns overall plant health score, sensor KPIs, alert counts,
    and system uptime for the dashboard overview widget.
    """
    return ai_service.get_dashboard_summary(db)
