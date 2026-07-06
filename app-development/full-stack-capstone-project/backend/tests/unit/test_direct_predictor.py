"""Unit test for DirectPredictor — learning goal: mock the boundary, test the logic.

We inject a fake model AND a fake session, so no MLflow/DB is involved; what we
actually test is OUR code: model selection, persistence call, latency measurement.
"""

from app.schemas import PredictRequest
from app.serving.direct import DirectPredictor
from tests.unit.test_schemas import VALID_FEATURES


class FakeModel:
    """Stands in for an MLflow pyfunc model; always predicts 42.0."""

    def predict(self, frame):
        return [42.0]


class FakeSession:
    """Stands in for a SQLAlchemy session; assigns the id a real DB would."""

    def add(self, row):
        row.id = 7  # the DB would autoincrement this

    def commit(self):
        pass


def test_predict_uses_injected_model_persists_and_measures_latency():
    predictor = DirectPredictor(models={"lightgbm": FakeModel()})
    req = PredictRequest(features=VALID_FEATURES, model="lightgbm")

    resp = predictor.predict(req, FakeSession())

    assert resp.predicted_price == 42.0
    assert resp.prediction_id == 7          # came back from the "persisted" row
    assert resp.serving_mode == "direct"
    assert resp.latency_ms > 0              # perf_counter always advances
