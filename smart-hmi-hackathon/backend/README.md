# ARIA Backend

> **ARIA — Adaptive Real-time Intelligence Assistant**
> FastAPI backend for the Smart HMI Hackathon project.

---

## Quick Start

```bash
# 1. Navigate to backend directory
cd backend

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open your browser at: **http://localhost:8000/docs**

---

## Architecture

```
backend/
├── app/
│   ├── main.py              ← FastAPI app entry point, CORS, routers
│   ├── database.py          ← SQLAlchemy engine, session, health check, init
│   ├── models/
│   │   ├── sensor.py        ← Sensor + SensorHistory ORM models
│   │   └── alert.py         ← Alert ORM model
│   ├── schemas/
│   │   ├── sensor_schema.py ← Pydantic request/response schemas
│   │   └── alert_schema.py  ← Pydantic request/response schemas
│   ├── services/
│   │   ├── sensor_service.py  ← Business logic for sensors
│   │   ├── alert_service.py   ← Business logic for alerts (prioritize, group)
│   │   └── ai_service.py      ← Predictive alerts, AI suggestions, role views
│   └── routes/
│       ├── sensors.py       ← GET|POST /api/sensors
│       ├── alerts.py        ← GET|POST /api/alerts
│       ├── predictive.py    ← GET /api/predictive-alerts, /api/ai-suggestions
│       └── roles.py         ← GET /api/role/operator|engineer|manager
├── requirements.txt
├── .env
└── README.md
```

---

## API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/` | Root — health + endpoint index |
| GET | `/health` | Health check |
| GET | `/api/sensors` | All sensors (with optional `?zone=Zone+A`) |
| GET | `/api/sensors/{id}` | Single sensor by ID |
| POST | `/api/sensors` | Create sensor |
| GET | `/api/alerts` | All alerts (prioritized: critical first) |
| GET | `/api/alerts?severity=critical` | Filter by severity |
| GET | `/api/alerts?grouped=true` | Alerts grouped by zone & severity |
| POST | `/api/alerts` | Create alert |
| GET | `/api/predictive-alerts` | AI time-to-breach predictions |
| GET | `/api/ai-suggestions` | Rule-based AI action suggestions |
| GET | `/api/dashboard-summary` | Plant health score + KPI summary |
| GET | `/api/role/operator` | Operator-tailored view |
| GET | `/api/role/engineer` | Engineer-tailored view |
| GET | `/api/role/manager` | Manager-tailored view |

---

## Data Source Fallback Logic

Every endpoint returns a `data_source` flag:

```json
{ "data_source": "database", "sensors": [...] }
{ "data_source": "mock",     "sensors": [...] }
```

**Logic:**
1. Try to query the database
2. If DB has data → serve real data (`"data_source": "database"`)
3. If DB is empty or unreachable → serve built-in mock data (`"data_source": "mock"`)
4. JSON shape is **identical** in both cases — frontend never needs to change

---

## Database Configuration

Edit `.env`:

```env
# SQLite (default — zero setup)
DATABASE_URL=sqlite:///./aria.db

# MySQL
DATABASE_URL=mysql+pymysql://username:password@localhost/aria_db
```

On first run, the backend automatically:
- Creates all tables via SQLAlchemy
- Seeds them from `../database/schema.sql`

---

## Git Commands

```bash
git add .
git commit -m "Added ARIA backend with DB connection and mock fallback"
git push origin main
```
