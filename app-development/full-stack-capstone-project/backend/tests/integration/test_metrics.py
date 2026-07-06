"""Metrics smoke test — learning goal: /metrics is an API too; assert on it.

Grafana dashboards query these exact series names and labels, so a rename
here would silently blank the dashboards — this test makes it loud instead.
"""

import pytest

from tests.unit.test_schemas import VALID_FEATURES

pytestmark = pytest.mark.integration


def test_prediction_metrics_are_exposed_with_labels(api_client):
    api_client.post("/predict", json={"features": VALID_FEATURES, "model": "linreg"})

    text = api_client.get("/metrics").text

    # Our domain metrics, labeled by model and serving_mode...
    assert 'predictions_total{model="linreg",serving_mode="direct"}' in text
    assert "prediction_latency_seconds_bucket" in text
    # ...plus the instrumentator's generic HTTP histogram.
    assert "http_request_duration_seconds" in text
