"""The serving seam: one tiny interface both modes implement.

`direct` (Tier A) and `streaming` (Tier B) each provide a Predictor. The API
layer only ever talks to this Protocol, which is what makes the SERVING_MODE
flag transparent to callers.
"""

from typing import Protocol

from app.schemas import PredictRequest


class Predictor(Protocol):
    def predict(self, req: PredictRequest) -> tuple[float, float]:
        """Return (predicted_price, model_latency_ms) for one request."""
        ...


def get_predictor(serving_mode: str) -> Predictor:
    """Factory: pick the implementation for the configured mode."""
    if serving_mode == "direct":
        # Imported here so `streaming` mode never pays the MLflow import cost.
        from app.serving.direct import DirectPredictor

        return DirectPredictor()
    if serving_mode == "streaming":
        raise NotImplementedError("streaming mode arrives in Tier B")
    raise ValueError(f"unknown serving mode: {serving_mode}")
