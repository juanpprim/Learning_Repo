"""Shared fixtures. The star: a REAL Postgres via testcontainers.

Learning goal — integration tests hit real infrastructure, not mocks. Docker
spins up a throwaway Postgres per test session and destroys it afterwards.
"""

import os

import pytest


@pytest.fixture(scope="session")
def postgres_url():
    """A live Postgres connection URL, or skip if Docker isn't available."""
    try:
        from testcontainers.postgres import PostgresContainer
    except ImportError:
        pytest.skip("testcontainers not installed")

    with PostgresContainer("postgres:16-alpine") as pg:
        yield pg.get_connection_url()  # e.g. postgresql+psycopg2://test:test@:32768/test


@pytest.fixture()
def api_client(postgres_url):
    """A FastAPI TestClient wired to the container DB and a FAKE predictor.

    The fake predictor keeps these tests about the API layer (validation,
    persistence, response shape) — model quality has its own tests.
    """
    # Point the app at the container BEFORE anything caches settings/engine.
    os.environ["DATABASE_URL"] = postgres_url
    from app import db, main
    from app.config import get_settings

    get_settings.cache_clear()  # drop any Settings built with the old URL
    db._engine = None           # force db.py to rebuild its engine lazily
    db._SessionLocal = None

    class FakePredictor:
        def predict(self, req):
            return 4_200_000.0, 0.1  # (price, model_latency_ms)

    main.app.dependency_overrides[main.predictor_dep] = lambda: FakePredictor()

    from fastapi.testclient import TestClient

    # Context manager runs the lifespan hook -> creates tables in the container.
    with TestClient(main.app) as client:
        yield client

    main.app.dependency_overrides.clear()
