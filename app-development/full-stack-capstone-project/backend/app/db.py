"""Database wiring: one SQLAlchemy engine + a session dependency for FastAPI.

Kept minimal on purpose — no Alembic migrations; tables are created at startup
with `Base.metadata.create_all` (fine for a learning project).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    """Parent class for all ORM models (see models_orm.py)."""


def make_engine(database_url: str | None = None):
    """Build an engine. Tests pass their own URL (a testcontainers Postgres)."""
    url = database_url or get_settings().DATABASE_URL
    # pool_pre_ping: quietly reconnect if Postgres restarted under us.
    return create_engine(url, pool_pre_ping=True)


# Lazily-created default engine/session factory used by the app.
_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        _engine = make_engine()
    return _engine


def get_session() -> Session:
    """FastAPI dependency: yields a session and always closes it."""
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine())
    session = _SessionLocal()
    try:
        yield session
    finally:
        session.close()
