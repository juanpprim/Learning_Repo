"""Streaming integration test — learning goal: async result delivery is testable.

The request really travels gateway -> Kafka -> consumer -> Postgres -> gateway.
(The consumer here is a thin stub thread playing the Spark job's role — same
message contract, same DB write; see conftest. The real Spark container is
exercised in the full-stack run, `make up-streaming`.)
"""

import pytest

from tests.unit.test_schemas import VALID_FEATURES

pytestmark = pytest.mark.integration


def test_streaming_round_trip(streaming_api_client):
    resp = streaming_api_client.post(
        "/predict", json={"features": VALID_FEATURES, "model": "linreg"}
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["serving_mode"] == "streaming"
    assert body["predicted_price"] == 4_200_000.0  # from the stub consumer

    # The row the consumer wrote is what the history endpoint serves.
    history = streaming_api_client.get("/predictions").json()
    row = next(r for r in history if r["id"] == body["prediction_id"])
    assert row["serving_mode"] == "streaming"


def test_streaming_latency_includes_queue_round_trip(streaming_api_client):
    resp = streaming_api_client.post(
        "/predict", json={"features": VALID_FEATURES, "model": "lightgbm"}
    )
    # Queue + consumer + poll cycle: must be visibly slower than in-process
    # (sub-ms) but comfortably under the 15s gateway timeout.
    assert 1 < resp.json()["latency_ms"] < 15_000
