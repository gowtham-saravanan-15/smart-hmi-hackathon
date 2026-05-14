"""
ARIA Backend — services/alert_service.py
Business logic for alerts.
DB-first with automatic mock data fallback.
Implements alarm prioritization and smart grouping.
"""

from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.schemas.alert_schema import AlertCreate


# ─────────────────────────────────────────────
#  MOCK DATA
# ─────────────────────────────────────────────
MOCK_ALERTS: List[Dict[str, Any]] = [
    {"id": 1, "sensor_id": 3, "title": "Critical: Pump 3 Overheating",     "description": "Pump 3 temperature at 88°C, exceeds 80°C limit.",           "severity": "critical", "zone": "Zone B", "status": "active", "created_at": "2026-05-14T11:45:00", "resolved_at": None},
    {"id": 2, "sensor_id": 7, "title": "Critical: Motor Vibration High",    "description": "Motor vibration at 6.8 mm/s — bearing failure imminent.",   "severity": "critical", "zone": "Zone B", "status": "active", "created_at": "2026-05-14T11:50:00", "resolved_at": None},
    {"id": 3, "sensor_id": 1, "title": "Warning: Pump 1 Temp Rising",       "description": "Pump 1 temperature at 72.5°C and climbing rapidly.",        "severity": "high",     "zone": "Zone A", "status": "active", "created_at": "2026-05-14T11:55:00", "resolved_at": None},
    {"id": 4, "sensor_id": 5, "title": "Warning: Valve 4 Pressure High",    "description": "Valve 4 at 4.9 bar, near maximum of 5.0 bar.",              "severity": "medium",   "zone": "Zone B", "status": "active", "created_at": "2026-05-14T12:00:00", "resolved_at": None},
    {"id": 5, "sensor_id": 2, "title": "Info: Pump 2 Maintenance Due",      "description": "Pump 2 scheduled maintenance in 48 hours.",                 "severity": "low",      "zone": "Zone A", "status": "active", "created_at": "2026-05-14T12:05:00", "resolved_at": None},
]

# Severity ordering
SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def _alert_to_dict(alert: Alert) -> Dict[str, Any]:
    return {
        "id": alert.id,
        "sensor_id": alert.sensor_id,
        "title": alert.title,
        "description": alert.description,
        "severity": alert.severity,
        "zone": alert.zone,
        "status": alert.status,
        "created_at": alert.created_at.isoformat() if alert.created_at else None,
        "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None,
    }


def _prioritize(alerts: List[Dict]) -> List[Dict]:
    """Sort alerts by severity (critical first) then by creation time."""
    return sorted(alerts, key=lambda a: (SEVERITY_ORDER.get(a["severity"], 99), a.get("created_at", "")))


def _group_by_zone(alerts: List[Dict]) -> Dict[str, List[Dict]]:
    """Group alerts by zone — smart grouping for the UI."""
    groups: Dict[str, List[Dict]] = {}
    for alert in alerts:
        zone = alert.get("zone", "Unknown")
        groups.setdefault(zone, []).append(alert)
    return groups


# ─────────────────────────────────────────────
#  SERVICE FUNCTIONS
# ─────────────────────────────────────────────

def get_all_alerts(db: Session) -> Dict[str, Any]:
    try:
        alerts = db.query(Alert).filter(Alert.status == "active").all()
        if alerts:
            alert_list = [_alert_to_dict(a) for a in alerts]
            prioritized = _prioritize(alert_list)
            return {
                "data_source": "database",
                "count": len(prioritized),
                "alerts": prioritized,
                "grouped_by_zone": _group_by_zone(prioritized),
            }
    except Exception:
        pass

    prioritized = _prioritize(MOCK_ALERTS)
    return {
        "data_source": "mock",
        "count": len(prioritized),
        "alerts": prioritized,
        "grouped_by_zone": _group_by_zone(prioritized),
    }


def get_alerts_by_severity(severity: str, db: Session) -> Dict[str, Any]:
    try:
        alerts = db.query(Alert).filter(
            Alert.severity == severity, Alert.status == "active"
        ).all()
        if alerts is not None:
            alert_list = [_alert_to_dict(a) for a in alerts]
            return {"data_source": "database", "severity": severity, "alerts": alert_list}
    except Exception:
        pass

    mock = [a for a in MOCK_ALERTS if a["severity"] == severity]
    return {"data_source": "mock", "severity": severity, "alerts": mock}


def create_alert(payload: AlertCreate, db: Session) -> Dict[str, Any]:
    try:
        alert = Alert(**payload.model_dump())
        db.add(alert)
        db.commit()
        db.refresh(alert)
        return {"data_source": "database", "alert": _alert_to_dict(alert)}
    except Exception as e:
        db.rollback()
        raise RuntimeError(f"DB write failed: {e}")


def get_grouped_alerts(db: Session) -> Dict[str, Any]:
    """Return alerts smartly grouped by zone and severity."""
    result = get_all_alerts(db)
    alerts = result["alerts"]
    grouped = {
        "by_zone": _group_by_zone(alerts),
        "by_severity": {
            "critical": [a for a in alerts if a["severity"] == "critical"],
            "high":     [a for a in alerts if a["severity"] == "high"],
            "medium":   [a for a in alerts if a["severity"] == "medium"],
            "low":      [a for a in alerts if a["severity"] == "low"],
        },
    }
    return {
        "data_source": result["data_source"],
        "total_alerts": result["count"],
        "grouped": grouped,
    }
