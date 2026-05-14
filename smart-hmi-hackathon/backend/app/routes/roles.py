"""
ARIA Backend — routes/roles.py
REST API controller for role-based view endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import ai_service

router = APIRouter(prefix="/api/role", tags=["Role-Based Views"])


@router.get("/operator", summary="Operator view — live sensor status and active alarms")
def operator_view(db: Session = Depends(get_db)):
    """
    Tailored for plant floor operators.
    Shows live sensor readings and critical/high alerts only.
    No analytics or predictions — keeps the view simple and actionable.
    """
    return ai_service.get_operator_view(db)


@router.get("/engineer", summary="Engineer view — predictive analytics and AI suggestions")
def engineer_view(db: Session = Depends(get_db)):
    """
    Tailored for process engineers.
    Shows full sensor detail, predictive alerts, trend data, and AI suggestions.
    """
    return ai_service.get_engineer_view(db)


@router.get("/manager", summary="Manager view — executive KPI dashboard")
def manager_view(db: Session = Depends(get_db)):
    """
    Tailored for plant managers.
    Shows high-level plant health score, KPIs, and zone summary.
    No raw sensor noise — pure executive visibility.
    """
    return ai_service.get_manager_view(db)
