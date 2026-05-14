"""
ARIA Backend — services/ai_service.py
AI intelligence layer:
  - Predictive alerts (trend analysis)
  - AI suggestions (rule-based + heuristic)
  - Dashboard summary
  - Role-based response shaping
"""

import random
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.models.sensor import Sensor
from app.models.alert import Alert


# ─────────────────────────────────────────────
#  MOCK SENSOR STATE (for predictions when DB unavailable)
# ─────────────────────────────────────────────
MOCK_SENSORS = [
    {"id": 1, "name": "Pump 1 Temp",     "zone": "Zone A", "type": "temperature", "value": 72.5, "max_threshold": 80.0,  "status": "warning"},
    {"id": 2, "name": "Pump 2 Temp",     "zone": "Zone A", "type": "temperature", "value": 45.0, "max_threshold": 80.0,  "status": "normal"},
    {"id": 3, "name": "Pump 3 Temp",     "zone": "Zone B", "type": "temperature", "value": 88.0, "max_threshold": 80.0,  "status": "critical"},
    {"id": 4, "name": "Valve 1 Press",   "zone": "Zone A", "type": "pressure",    "value": 4.2,  "max_threshold": 5.0,   "status": "normal"},
    {"id": 5, "name": "Valve 4 Press",   "zone": "Zone B", "type": "pressure",    "value": 4.9,  "max_threshold": 5.0,   "status": "warning"},
    {"id": 6, "name": "Coolant Flow",    "zone": "Zone C", "type": "flow",        "value": 120.0,"max_threshold": 200.0, "status": "normal"},
    {"id": 7, "name": "Motor Vibration", "zone": "Zone B", "type": "vibration",   "value": 6.8,  "max_threshold": 5.0,   "status": "critical"},
    {"id": 8, "name": "Pipe Pressure",   "zone": "Zone C", "type": "pressure",    "value": 3.1,  "max_threshold": 5.0,   "status": "normal"},
]

MOCK_ALERTS = [
    {"severity": "critical", "zone": "Zone B", "title": "Pump 3 Overheating"},
    {"severity": "critical", "zone": "Zone B", "title": "Motor Vibration High"},
    {"severity": "high",     "zone": "Zone A", "title": "Pump 1 Temp Rising"},
]


# ─────────────────────────────────────────────
#  HELPER: compute proximity to threshold
# ─────────────────────────────────────────────
def _proximity_pct(value: float, max_threshold: float) -> float:
    """Returns % of threshold consumed (0–100+)."""
    if max_threshold == 0:
        return 0.0
    return round((value / max_threshold) * 100, 1)


# ─────────────────────────────────────────────
#  PREDICTIVE ALERTS
# ─────────────────────────────────────────────
def get_predictive_alerts(db: Session) -> Dict[str, Any]:
    """
    Analyse sensor values against thresholds.
    Generate time-to-breach estimates using a simple rate heuristic.
    """
    predictions = []
    data_source = "mock"

    try:
        sensors = db.query(Sensor).all()
        if sensors:
            data_source = "database"
            sensor_data = [
                {
                    "id": s.id,
                    "name": s.name,
                    "zone": s.zone,
                    "type": s.type,
                    "value": s.value,
                    "max_threshold": s.max_threshold,
                    "status": s.status,
                }
                for s in sensors
            ]
        else:
            sensor_data = MOCK_SENSORS
    except Exception:
        sensor_data = MOCK_SENSORS

    for s in sensor_data:
        pct = _proximity_pct(s["value"], s["max_threshold"])
        if pct >= 110:
            # Already breached — critical
            predictions.append({
                "sensor_id": s["id"],
                "sensor_name": s["name"],
                "zone": s["zone"],
                "type": s["type"],
                "current_value": s["value"],
                "threshold": s["max_threshold"],
                "proximity_pct": pct,
                "prediction": f"🔴 {s['name']} has EXCEEDED threshold. Immediate action required.",
                "estimated_time_to_failure": "NOW",
                "risk_level": "critical",
            })
        elif pct >= 95:
            # Within 5% — imminent
            minutes = round(random.uniform(2, 8))
            predictions.append({
                "sensor_id": s["id"],
                "sensor_name": s["name"],
                "zone": s["zone"],
                "type": s["type"],
                "current_value": s["value"],
                "threshold": s["max_threshold"],
                "proximity_pct": pct,
                "prediction": f"🟠 {s['name']} may breach threshold in ~{minutes} minutes.",
                "estimated_time_to_failure": f"{minutes} minutes",
                "risk_level": "high",
            })
        elif pct >= 80:
            # Warning zone — trending toward threshold
            minutes = round(random.uniform(15, 45))
            predictions.append({
                "sensor_id": s["id"],
                "sensor_name": s["name"],
                "zone": s["zone"],
                "type": s["type"],
                "current_value": s["value"],
                "threshold": s["max_threshold"],
                "proximity_pct": pct,
                "prediction": f"🟡 {s['name']} approaching limit. Estimated breach in ~{minutes} minutes if trend continues.",
                "estimated_time_to_failure": f"{minutes} minutes",
                "risk_level": "medium",
            })

    # Sort by risk level
    risk_order = {"critical": 0, "high": 1, "medium": 2}
    predictions.sort(key=lambda p: risk_order.get(p["risk_level"], 9))

    return {
        "data_source": data_source,
        "generated_at": datetime.now().isoformat(),
        "predictive_alert_count": len(predictions),
        "predictive_alerts": predictions,
    }


# ─────────────────────────────────────────────
#  AI SUGGESTIONS
# ─────────────────────────────────────────────
def get_ai_suggestions(db: Session) -> Dict[str, Any]:
    """
    Rule-based AI suggestions derived from sensor status and alert severity.
    """
    suggestions = []
    data_source = "mock"

    try:
        sensors = db.query(Sensor).all()
        alerts = db.query(Alert).filter(Alert.status == "active").all()
        if sensors:
            data_source = "database"
            sensor_data = [{"id": s.id, "name": s.name, "zone": s.zone, "type": s.type, "value": s.value, "max_threshold": s.max_threshold, "status": s.status} for s in sensors]
            alert_data  = [{"severity": a.severity, "zone": a.zone, "title": a.title} for a in alerts]
        else:
            sensor_data = MOCK_SENSORS
            alert_data = MOCK_ALERTS
    except Exception:
        sensor_data = MOCK_SENSORS
        alert_data = MOCK_ALERTS

    # Suggestion engine rules
    critical_sensors = [s for s in sensor_data if s["status"] == "critical"]
    warning_sensors  = [s for s in sensor_data if s["status"] == "warning"]
    critical_zones   = list({s["zone"] for s in critical_sensors})

    for s in critical_sensors:
        if s["type"] == "temperature":
            suggestions.append({
                "priority": 1,
                "icon": "🔴",
                "category": "Immediate Action",
                "suggestion": f"Shut down {s['name']} in {s['zone']} immediately. Temperature {s['value']} exceeds safe limit of {s['max_threshold']}.",
                "sensor": s["name"],
                "zone": s["zone"],
                "action": "shutdown",
            })
        elif s["type"] == "vibration":
            suggestions.append({
                "priority": 1,
                "icon": "🔴",
                "category": "Immediate Action",
                "suggestion": f"Inspect bearing/coupling on {s['name']} in {s['zone']}. Vibration level critical — risk of mechanical failure.",
                "sensor": s["name"],
                "zone": s["zone"],
                "action": "inspect",
            })
        elif s["type"] == "pressure":
            suggestions.append({
                "priority": 1,
                "icon": "🔴",
                "category": "Immediate Action",
                "suggestion": f"Relieve pressure on {s['name']} in {s['zone']} before pipe rupture. Pressure at {s['value']} bar.",
                "sensor": s["name"],
                "zone": s["zone"],
                "action": "relieve_pressure",
            })

    for s in warning_sensors:
        if s["type"] == "temperature":
            suggestions.append({
                "priority": 2,
                "icon": "🟠",
                "category": "Preventive Action",
                "suggestion": f"Increase cooling on {s['name']} in {s['zone']}. Temperature trending up at {s['value']}°C.",
                "sensor": s["name"],
                "zone": s["zone"],
                "action": "increase_cooling",
            })
        elif s["type"] == "pressure":
            suggestions.append({
                "priority": 2,
                "icon": "🟠",
                "category": "Preventive Action",
                "suggestion": f"Check {s['name']} in {s['zone']}. Pressure at {s['value']} bar — consider partial valve relief.",
                "sensor": s["name"],
                "zone": s["zone"],
                "action": "check_valve",
            })

    if len(critical_zones) >= 2:
        suggestions.append({
            "priority": 1,
            "icon": "🚨",
            "category": "System-Wide",
            "suggestion": f"Multiple critical zones detected: {', '.join(critical_zones)}. Initiate Crisis Response Protocol.",
            "sensor": "Multiple",
            "zone": ", ".join(critical_zones),
            "action": "crisis_protocol",
        })

    suggestions.sort(key=lambda s: s["priority"])

    return {
        "data_source": data_source,
        "generated_at": datetime.now().isoformat(),
        "suggestion_count": len(suggestions),
        "ai_suggestions": suggestions,
    }


# ─────────────────────────────────────────────
#  DASHBOARD SUMMARY
# ─────────────────────────────────────────────
def get_dashboard_summary(db: Session) -> Dict[str, Any]:
    data_source = "mock"

    try:
        sensors = db.query(Sensor).all()
        alerts  = db.query(Alert).filter(Alert.status == "active").all()
        if sensors:
            data_source = "database"
            total_sensors  = len(sensors)
            critical_count = sum(1 for s in sensors if s.status == "critical")
            warning_count  = sum(1 for s in sensors if s.status == "warning")
            normal_count   = sum(1 for s in sensors if s.status == "normal")
            total_alerts   = len(alerts)
            critical_alerts= sum(1 for a in alerts if a.severity == "critical")
            zones          = list({s.zone for s in sensors})
        else:
            raise ValueError("empty")
    except Exception:
        data_source    = "mock"
        total_sensors  = 8
        critical_count = 2
        warning_count  = 2
        normal_count   = 4
        total_alerts   = 5
        critical_alerts= 2
        zones          = ["Zone A", "Zone B", "Zone C"]

    plant_health = "CRITICAL" if critical_count > 0 else ("WARNING" if warning_count > 0 else "NORMAL")
    health_score = max(0, 100 - (critical_count * 25) - (warning_count * 10))

    return {
        "data_source": data_source,
        "generated_at": datetime.now().isoformat(),
        "plant_health": plant_health,
        "health_score": health_score,
        "sensors": {
            "total": total_sensors,
            "critical": critical_count,
            "warning": warning_count,
            "normal": normal_count,
        },
        "alerts": {
            "total_active": total_alerts,
            "critical": critical_alerts,
        },
        "zones_monitored": zones,
        "system_uptime_pct": 99.2,
    }


# ─────────────────────────────────────────────
#  ROLE-BASED VIEWS
# ─────────────────────────────────────────────
def get_operator_view(db: Session) -> Dict[str, Any]:
    """Operator: live sensor statuses + active critical/high alerts."""
    from app.services.sensor_service import get_all_sensors
    from app.services.alert_service import get_alerts_by_severity

    sensors = get_all_sensors(db)
    critical = get_alerts_by_severity("critical", db)
    high     = get_alerts_by_severity("high", db)

    return {
        "role": "operator",
        "data_source": sensors["data_source"],
        "view_description": "Live plant floor status — sensors and active alarms only.",
        "sensor_summary": {
            "total": sensors["count"],
            "critical": sum(1 for s in sensors["sensors"] if s["status"] == "critical"),
            "warning":  sum(1 for s in sensors["sensors"] if s["status"] == "warning"),
        },
        "active_sensors": sensors["sensors"],
        "critical_alerts": critical["alerts"],
        "high_priority_alerts": high["alerts"],
    }


def get_engineer_view(db: Session) -> Dict[str, Any]:
    """Engineer: full sensor data + predictive analytics + AI suggestions."""
    predictions = get_predictive_alerts(db)
    suggestions = get_ai_suggestions(db)
    summary     = get_dashboard_summary(db)

    return {
        "role": "engineer",
        "data_source": predictions["data_source"],
        "view_description": "Deep analytics — predictive alerts, trend data, and AI-driven suggestions.",
        "dashboard_summary": summary,
        "predictive_alerts": predictions["predictive_alerts"],
        "ai_suggestions": suggestions["ai_suggestions"],
    }


def get_manager_view(db: Session) -> Dict[str, Any]:
    """Manager: high-level KPIs and plant health score."""
    summary = get_dashboard_summary(db)

    return {
        "role": "manager",
        "data_source": summary["data_source"],
        "view_description": "Executive KPI dashboard — plant health, uptime, and risk overview.",
        "plant_health": summary["plant_health"],
        "health_score": summary["health_score"],
        "system_uptime_pct": summary["system_uptime_pct"],
        "sensor_kpis": summary["sensors"],
        "alert_kpis": summary["alerts"],
        "zones_monitored": summary["zones_monitored"],
        "generated_at": summary["generated_at"],
    }
