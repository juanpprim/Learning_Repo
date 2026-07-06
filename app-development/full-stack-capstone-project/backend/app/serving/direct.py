"""Direct (in-process) serving: load both MLflow models once, predict locally.

Lowest-latency path — no queue, no network hop. Used for dev, tests, and as the
synchronous baseline in the load study.
"""

import time

import mlflow.pyfunc

from app.config import get_settings
from app.schemas import PredictRequest


class DirectPredictor:
    def __init__(self, models: dict | None = None):
        # Tests inject fake models here; production lazy-loads from MLflow.
        self._models = models or {}

    def _load(self, name: str):
        """Fetch a registered model by its @production alias, once, then cache."""
        if name not in self._models:
            mlflow.set_tracking_uri(get_settings().MLFLOW_TRACKING_URI)
            # Same URI convention the Spark job will use in Tier B — never copy weights.
            self._models[name] = mlflow.pyfunc.load_model(f"models:/{name}@production")
        return self._models[name]

    def predict(self, req: PredictRequest) -> tuple[float, float]:
        model = self._load(req.model)
        start = time.perf_counter()
        # to_frame() reshapes the request into the training-data format.
        prediction = model.predict(req.features.to_frame())
        latency_ms = (time.perf_counter() - start) * 1000
        return float(prediction[0]), latency_ms
