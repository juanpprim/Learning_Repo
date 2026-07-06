"""Shared fixtures. The stars: REAL Postgres and Kafka via testcontainers.

Learning goal — integration tests hit real infrastructure, not mocks. Docker
spins up throwaway containers per test session and destroys them afterwards.
"""

import json
import os
import threading

import pytest


@pytest.fixture(scope="session")
def postgres_url():
    """A live Postgres connection URL (one container for the whole session)."""
    from testcontainers.postgres import PostgresContainer

    with PostgresContainer("postgres:16-alpine") as pg:
        yield pg.get_connection_url()  # e.g. postgresql+psycopg2://test:test@:32768/test


@pytest.fixture(scope="session")
def kafka_bootstrap():
    """A live single-broker Kafka; yields its bootstrap server address."""
    from testcontainers.kafka import KafkaContainer

    with KafkaContainer("confluentinc/cp-kafka:7.6.1") as kafka:
        yield kafka.get_bootstrap_server()


def _fresh_app(postgres_url: str, serving_mode: str, bootstrap: str | None = None):
    """(Re)configure the FastAPI app for a test: env, settings cache, engine."""
    os.environ["DATABASE_URL"] = postgres_url
    os.environ["SERVING_MODE"] = serving_mode
    if bootstrap:
        os.environ["KAFKA_BOOTSTRAP_SERVERS"] = bootstrap

    from app import db, main
    from app.config import get_settings

    get_settings.cache_clear()  # drop Settings built with old env values
    db._engine = None           # force db.py to rebuild its engine lazily
    db._SessionLocal = None
    main._predictor = None      # forget any predictor from a previous test
    return main


@pytest.fixture()
def api_client(postgres_url):
    """TestClient in DIRECT mode, with a FAKE predictor.

    The fake keeps these tests about the API layer (validation, persistence,
    response shape) — model quality has its own tests.
    """
    main = _fresh_app(postgres_url, "direct")

    class FakePredictor:
        """Mimics DirectPredictor's contract without any MLflow model."""

        def predict(self, req, session):
            from app.models_orm import Prediction
            from app.schemas import PredictResponse

            row = Prediction(
                model=req.model,
                serving_mode="direct",
                features=req.features.model_dump(),
                predicted_price=4_200_000.0,
                latency_ms=0.1,
            )
            session.add(row)
            session.commit()
            return PredictResponse(
                prediction_id=row.id,
                predicted_price=4_200_000.0,
                model=req.model,
                serving_mode="direct",
                latency_ms=0.1,
            )

    main.app.dependency_overrides[main.predictor_dep] = lambda: FakePredictor()

    from fastapi.testclient import TestClient

    # Context manager runs the lifespan hook -> creates tables in the container.
    with TestClient(main.app) as client:
        yield client

    main.app.dependency_overrides.clear()


def _run_stub_consumer(bootstrap: str, db_url: str, stop: threading.Event):
    """A thin stand-in for the Spark job: consume -> 'predict' -> INSERT row.

    Same message contract and same DB write as spark/consumer.py, minus Spark —
    which lets the streaming round trip be tested quickly inside pytest.
    """
    from confluent_kafka import Consumer
    from sqlalchemy import create_engine, text

    consumer = Consumer(
        {
            "bootstrap.servers": bootstrap,
            "group.id": "stub-consumer",
            "auto.offset.reset": "earliest",
        }
    )
    consumer.subscribe(["prediction-requests"])
    engine = create_engine(db_url)

    while not stop.is_set():
        msg = consumer.poll(0.2)
        if msg is None or msg.error():
            continue
        payload = json.loads(msg.value())
        with engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO predictions (created_at, request_id, model, serving_mode,"
                    " features, predicted_price, latency_ms)"
                    " VALUES (now(), :rid, :model, 'streaming', :features, 4200000.0, 0)"
                ),
                {
                    "rid": payload["request_id"],
                    "model": payload["model"],
                    "features": json.dumps(payload["features"]),
                },
            )
    consumer.close()
    engine.dispose()


@pytest.fixture()
def streaming_api_client(postgres_url, kafka_bootstrap):
    """TestClient in STREAMING mode with the REAL StreamingPredictor.

    Messages travel through a real Kafka broker; a stub consumer thread plays
    the Spark job's role so the gateway's publish-and-wait logic is exercised
    end to end.
    """
    main = _fresh_app(postgres_url, "streaming", bootstrap=kafka_bootstrap)

    from fastapi.testclient import TestClient

    with TestClient(main.app) as client:  # lifespan creates the tables first...
        stop = threading.Event()
        thread = threading.Thread(
            target=_run_stub_consumer, args=(kafka_bootstrap, postgres_url, stop), daemon=True
        )
        thread.start()  # ...then the consumer starts inserting into them
        try:
            yield client
        finally:
            stop.set()
            thread.join(timeout=5)

    # Leave direct-mode defaults for whichever test runs next.
    os.environ["SERVING_MODE"] = "direct"
    from app.config import get_settings

    get_settings.cache_clear()
