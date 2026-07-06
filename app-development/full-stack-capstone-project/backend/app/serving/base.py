"""The serving seam: one tiny interface both modes implement.

Each Predictor is responsible for the WHOLE serving job — produce a price,
make sure a `predictions` row exists, and return the finished response:

- direct    (Tier A): call the model in-process, insert the row itself.
- streaming (Tier B): publish to Kafka; the Spark consumer predicts and
                      inserts the row; the predictor waits for it to appear.

The API layer only ever talks to this Protocol, which is what makes the
SERVING_MODE flag transparent to callers.
"""

from typing import Protocol

from sqlalchemy.orm import Session

from app.schemas import PredictRequest, PredictResponse


class Predictor(Protocol):
    def predict(self, req: PredictRequest, session: Session) -> PredictResponse:
        """Serve one request end-to-end (predict + persist + respond)."""
        ...


def get_predictor(serving_mode: str) -> Predictor:
    """Factory: pick the implementation for the configured mode."""
    # Imports live here so each mode only pays for what it uses.
    if serving_mode == "direct":
        from app.serving.direct import DirectPredictor

        return DirectPredictor()
    if serving_mode == "streaming":
        from app.serving.streaming import StreamingPredictor

        return StreamingPredictor()
    raise ValueError(f"unknown serving mode: {serving_mode}")
