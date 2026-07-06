"""Edge-hardening tests (Tier C) — auth and rate limiting are behavior, so
they get tests like any other behavior.
"""

import pytest

from tests.unit.test_schemas import VALID_FEATURES

pytestmark = pytest.mark.integration

PAYLOAD = {"features": VALID_FEATURES, "model": "linreg"}


@pytest.fixture()
def hardened_client(postgres_url, monkeypatch):
    """A client whose app requires an API key and allows only 3 req/min."""
    monkeypatch.setenv("API_KEY", "secret-key")
    monkeypatch.setenv("RATE_LIMIT", "3/minute")

    from tests.conftest import _fresh_app

    main = _fresh_app(postgres_url, "direct")

    class FakePredictor:
        def predict(self, req, session):
            from app.models_orm import Prediction
            from app.schemas import PredictResponse

            row = Prediction(
                model=req.model, serving_mode="direct",
                features=req.features.model_dump(),
                predicted_price=1.0, latency_ms=0.1,
            )
            session.add(row)
            session.commit()
            return PredictResponse(
                prediction_id=row.id, predicted_price=1.0,
                model=req.model, serving_mode="direct", latency_ms=0.1,
            )

    main.app.dependency_overrides[main.predictor_dep] = lambda: FakePredictor()

    from fastapi.testclient import TestClient

    with TestClient(main.app) as client:
        yield client
    main.app.dependency_overrides.clear()


def test_missing_api_key_is_401(hardened_client):
    assert hardened_client.post("/predict", json=PAYLOAD).status_code == 401


def test_wrong_api_key_is_401(hardened_client):
    resp = hardened_client.post("/predict", json=PAYLOAD, headers={"X-API-Key": "nope"})
    assert resp.status_code == 401


def test_rate_limit_sheds_load_with_429(hardened_client):
    headers = {"X-API-Key": "secret-key"}
    # The first 3 requests fit the window...
    for _ in range(3):
        assert hardened_client.post("/predict", json=PAYLOAD, headers=headers).status_code == 200
    # ...the 4th is shed at the ingress before touching model or queue.
    assert hardened_client.post("/predict", json=PAYLOAD, headers=headers).status_code == 429


def test_health_needs_no_key(hardened_client):
    # Probes and dashboards must keep working without credentials.
    assert hardened_client.get("/health").status_code == 200
