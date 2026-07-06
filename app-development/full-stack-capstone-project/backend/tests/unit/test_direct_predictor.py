"""Unit test for DirectPredictor — learning goal: mock the boundary, test the logic.

We inject a fake model so no MLflow/network is involved; what we actually test
is OUR code: model selection, price extraction, latency measurement.
"""

from app.schemas import PredictRequest
from app.serving.direct import DirectPredictor
from tests.unit.test_schemas import VALID_FEATURES


class FakeModel:
    """Stands in for an MLflow pyfunc model; always predicts 42.0."""

    def predict(self, frame):
        return [42.0]


def test_predict_uses_injected_model_and_measures_latency():
    predictor = DirectPredictor(models={"lightgbm": FakeModel()})
    req = PredictRequest(features=VALID_FEATURES, model="lightgbm")

    price, latency_ms = predictor.predict(req)

    assert price == 42.0
    assert latency_ms > 0  # perf_counter always advances
