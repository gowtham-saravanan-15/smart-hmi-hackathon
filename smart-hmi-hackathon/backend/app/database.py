"""
ARIA Backend — database.py
SQLAlchemy engine + session factory.
Supports SQLite (default) and MySQL via DATABASE_URL env var.
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./aria.db")

# SQLite needs check_same_thread=False; other drivers don't need it
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a DB session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_health() -> bool:
    """
    Returns True if the DB is reachable and tables have data.
    Used to decide whether to serve real data or mock data.
    """
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM sensors"))
            count = result.scalar()
            return count is not None and count > 0
    except Exception:
        return False


def init_db():
    """Create all tables (if they don't exist) and optionally seed from schema.sql."""
    from app.models import sensor, alert  # noqa: F401 — import so Base sees them
    Base.metadata.create_all(bind=engine)

    # If the database is brand new, seed it from schema.sql
    try:
        with engine.connect() as conn:
            count = conn.execute(text("SELECT COUNT(*) FROM sensors")).scalar()
            if count == 0:
                schema_path = os.path.join(
                    os.path.dirname(__file__), "..", "..", "database", "schema.sql"
                )
                if os.path.exists(schema_path):
                    with open(schema_path, "r") as f:
                        raw_sql = f.read()
                    # Execute statement by statement (skip blank lines and comments)
                    statements = [
                        s.strip() for s in raw_sql.split(";") if s.strip() and not s.strip().startswith("--")
                    ]
                    for stmt in statements:
                        try:
                            conn.execute(text(stmt))
                        except Exception:
                            pass  # ignore CREATE TABLE IF NOT EXISTS duplicates
                    conn.commit()
    except Exception:
        pass  # tables not yet created — init_db will handle it on next call
