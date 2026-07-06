"""Streaming serving: publish to Kafka, let Spark predict, wait for the row.

The request travels:  gateway -> `prediction-requests` -> Spark consumer
(predicts + INSERTs into Postgres) -> gateway sees the row appear -> responds.

Returning via a short poll on the result store is deliberately the simplest
correct mechanism (the spec's "poll first, SSE later" advice). The measured
latency therefore includes the whole queue round trip — that's the point.
"""

import json
import time
import uuid

from confluent_kafka import Producer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models_orm import Prediction
from app.schemas import PredictRequest, PredictResponse


class StreamingPredictor:
    def __init__(self, producer: Producer | None = None):
        settings = get_settings()
        # One producer per process; confluent-kafka is thread-safe.
        self._producer = producer or Producer(
            {"bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS}
        )
        self._topic = settings.TOPIC_REQUESTS
        self._timeout_s = settings.STREAMING_TIMEOUT_S

    def predict(self, req: PredictRequest, session: Session) -> PredictResponse:
        # request_id is the correlation key between our message and the row
        # the Spark consumer will eventually write.
        request_id = str(uuid.uuid4())
        payload = {
            "request_id": request_id,
            "model": req.model,
            "features": req.features.model_dump(),
        }

        start = time.perf_counter()
        # Key by request_id so retries of the same request land on the same
        # partition (ordering per request).
        self._producer.produce(self._topic, key=request_id, value=json.dumps(payload))
        self._producer.flush(5)

        row = self._wait_for_row(session, request_id)
        latency_ms = (time.perf_counter() - start) * 1000

        return PredictResponse(
            prediction_id=row.id,
            predicted_price=row.predicted_price,
            model=req.model,
            serving_mode="streaming",
            latency_ms=latency_ms,  # full round trip: queue + Spark + Postgres
        )

    def _wait_for_row(self, session: Session, request_id: str) -> Prediction:
        """Short-poll Postgres until the consumer's row shows up (or time out)."""
        deadline = time.monotonic() + self._timeout_s
        while time.monotonic() < deadline:
            row = session.execute(
                select(Prediction).where(Prediction.request_id == request_id)
            ).scalar_one_or_none()
            if row is not None:
                return row
            session.rollback()  # end the snapshot so the next SELECT sees new rows
            time.sleep(0.05)
        raise TimeoutError(
            f"no result for request {request_id} within {self._timeout_s}s "
            "(is the Spark consumer running?)"
        )
