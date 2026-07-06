"""API integration tests — TestClient + real Postgres + stubbed model.

Learning goal: this layer proves request -> validation -> persistence ->
response works end to end inside the backend, without any ML dependency.
"""

import pytest

from tests.unit.test_schemas import VALID_FEATURES

pytestmark = pytest.mark.integration


def test_predict_persists_and_responds(api_client):
    resp = api_client.post("/predict", json={"features": VALID_FEATURES, "model": "linreg"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["predicted_price"] == 4_200_000.0  # from the fake predictor
    assert body["model"] == "linreg"
    assert body["serving_mode"] == "direct"
    assert body["latency_ms"] > 0

    # The prediction must now be in the history endpoint (i.e., in Postgres).
    history = api_client.get("/predictions").json()
    assert any(row["id"] == body["prediction_id"] for row in history)


def test_invalid_body_is_422(api_client):
    bad = {**VALID_FEATURES, "bedrooms": -1}
    resp = api_client.post("/predict", json={"features": bad})
    assert resp.status_code == 422  # FastAPI/Pydantic rejects it before our code runs


def test_health(api_client):
    assert api_client.get("/health").json() == {"status": "ok"}
