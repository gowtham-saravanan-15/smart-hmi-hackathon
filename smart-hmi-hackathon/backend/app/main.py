"""
ARIA Backend — main.py
FastAPI application entry point.
ARIA — Adaptive Real-time Intelligence Assistant
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.database import init_db, check_db_health
from app.routes import sensors, alerts, predictive, roles

# ─────────────────────────────────────────────
#  APPLICATION FACTORY
# ─────────────────────────────────────────────
app = FastAPI(
    title="ARIA — Adaptive Real-time Intelligence Assistant",
    description=(
        "Backend API for ARIA: industrial HMI platform with AI-powered "
        "alarm management, predictive analytics, and role-based dashboards."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─────────────────────────────────────────────
#  CORS — allow all origins for hackathon dev
#  (restrict to your frontend URL in production)
# ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Replace with ["http://localhost:3000"] in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
#  INCLUDE ROUTERS
# ─────────────────────────────────────────────
app.include_router(sensors.router)
app.include_router(alerts.router)
app.include_router(predictive.router)
app.include_router(roles.router)


# ─────────────────────────────────────────────
#  STARTUP EVENT — create tables and seed DB
# ─────────────────────────────────────────────
@app.on_event("startup")
def on_startup():
    print("[ARIA] Backend starting up...")
    init_db()
    is_healthy = check_db_health()
    if is_healthy:
        print("[ARIA] Database connected -- serving real data.")
    else:
        print("[ARIA] Database empty or unreachable -- mock data fallback active.")


# ─────────────────────────────────────────────
#  ROOT ENDPOINT
# ─────────────────────────────────────────────
@app.get("/", tags=["Root"])
def root():
    db_status = "connected" if check_db_health() else "mock_fallback"
    return JSONResponse({
        "project": "ARIA — Adaptive Real-time Intelligence Assistant",
        "version": "1.0.0",
        "status": "running",
        "database": db_status,
        "docs": "/docs",
        "endpoints": {
            "sensors":          "GET|POST /api/sensors",
            "alerts":           "GET|POST /api/alerts",
            "predictive":       "GET /api/predictive-alerts",
            "ai_suggestions":   "GET /api/ai-suggestions",
            "dashboard":        "GET /api/dashboard-summary",
            "role_operator":    "GET /api/role/operator",
            "role_engineer":    "GET /api/role/engineer",
            "role_manager":     "GET /api/role/manager",
        },
    })


@app.get("/health", tags=["Root"])
def health():
    return {"status": "ok", "database": "connected" if check_db_health() else "mock_fallback"}
