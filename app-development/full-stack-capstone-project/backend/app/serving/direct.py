"""Direct (in-process) serving: load both MLflow models once, predict locally.

Lowest-latency path — no queue, no network hop. Used for dev, tests, and as the
synchronous baseline in the load study.
"""

import time

import mlflow.pyfunc
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models_orm import Prediction
from app.schemas import PredictRequest, PredictResponse


class DirectPredictor:
    def __init__(self, models: dict | None = None):
        # Tests inject fake models here; production lazy-loads from MLflow.
        self._models = models or {}

    def _load(self, name: str):
        """Fetch a registered model by its @production alias, once, then cache."""
        if name not in self._models:
            mlflow.set_tracking_uri(get_settings().MLFLOW_TRACKING_URI)
            # Same URI convention the Spark job uses — never copy weights.
            self._models[name] = mlflow.pyfunc.load_model(f"models:/{name}@production")
        return self._models[name]

    def predict(self, req: PredictRequest, session: Session) -> PredictResponse:
        model = self._load(req.model)

        # Time the whole serving path (model + persistence): that is the number
        # the direct-vs-streaming load study compares.
        start = time.perf_counter()
        price = float(model.predict(req.features.to_frame())[0])

        row = Prediction(
            model=req.model,
            serving_mode="direct",
            features=req.features.model_dump(),
            predicted_price=price,
            latency_ms=0.0,  # filled just below, once the clock stops
        )
        session.add(row)
        session.commit()

        latency_ms = (time.perf_counter() - start) * 1000
        row.latency_ms = latency_ms
        session.commit()

        return PredictResponse(
            prediction_id=row.id,
            predicted_price=price,
            model=req.model,
            serving_mode="direct",
            latency_ms=latency_ms,
        )
