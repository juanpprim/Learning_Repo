"""FastAPI gateway: /predict, /predictions, /health, /metrics.

The route handlers are thin on purpose — validation lives in schemas.py,
model calls live behind the Predictor seam, persistence is a plain ORM insert.
"""

import time
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import Base, get_engine, get_session
from app.models_orm import Prediction
from app.schemas import PredictionRecord, PredictRequest, PredictResponse
from app.serving.base import Predictor, get_predictor

# Cached predictor (loads models once). Tests override via dependency_overrides.
_predictor: Predictor | None = None


def predictor_dep() -> Predictor:
    global _predictor
    if _predictor is None:
        _predictor = get_predictor(get_settings().SERVING_MODE)
    return _predictor


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables at startup — simplest possible "migration" strategy.
    Base.metadata.create_all(get_engine())
    yield


app = FastAPI(title="Real-Time ML Platform", lifespan=lifespan)

# The React dev server runs on another port, so allow cross-origin calls.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exposes GET /metrics with request-latency histograms for Prometheus (Tier B).
Instrumentator().instrument(app).expose(app)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(
    req: PredictRequest,
    session: Session = Depends(get_session),
    predictor: Predictor = Depends(predictor_dep),
) -> PredictResponse:
    settings = get_settings()

    # Time the WHOLE serving path (model + persistence), not just the model —
    # that is the number the direct-vs-streaming load study compares.
    start = time.perf_counter()
    price, _model_ms = predictor.predict(req)

    # Persist so the frontend history list (and later drift reports) can read it.
    row = Prediction(
        model=req.model,
        serving_mode=settings.SERVING_MODE,
        features=req.features.model_dump(),
        predicted_price=price,
        latency_ms=0.0,  # placeholder, updated right after we stop the clock
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
        serving_mode=settings.SERVING_MODE,
        latency_ms=latency_ms,
    )


@app.get("/predictions", response_model=list[PredictionRecord])
def list_predictions(limit: int = 20, session: Session = Depends(get_session)):
    rows = session.execute(
        select(Prediction).order_by(Prediction.id.desc()).limit(limit)
    ).scalars()
    return [
        PredictionRecord(
            id=r.id,
            created_at=r.created_at.isoformat(),
            model=r.model,
            serving_mode=r.serving_mode,
            features=r.features,
            predicted_price=r.predicted_price,
            latency_ms=r.latency_ms,
        )
        for r in rows
    ]
