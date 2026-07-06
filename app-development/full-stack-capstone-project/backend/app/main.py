"""FastAPI gateway: /predict, /predictions, /health, /metrics.

The route handlers are thin on purpose — validation lives in schemas.py,
model calls live behind the Predictor seam, persistence is a plain ORM insert.
"""

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app import drift, explain, metrics
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
    engine = get_engine()
    Base.metadata.create_all(engine)
    # Poor man's migration: create_all never ALTERs an existing table, so add
    # columns introduced after Tier A here. (A real project would use Alembic.)
    with engine.begin() as conn:
        conn.execute(
            text("ALTER TABLE predictions ADD COLUMN IF NOT EXISTS request_id VARCHAR(36)")
        )
    yield


app = FastAPI(title="Real-Time ML Platform", lifespan=lifespan)

# --- edge hardening (Tier C) -------------------------------------------------
# Rate limiting = load shedding at the ingress: past the limit, clients get an
# instant 429 instead of piling onto the model/queue. Limit is read per-request
# so tests can tighten it via env without rebuilding the app.
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Minimal auth: a shared API key header. Empty API_KEY = disabled (dev)."""
    expected = get_settings().API_KEY
    if expected and x_api_key != expected:
        raise HTTPException(status_code=401, detail="invalid or missing API key")

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


@app.post("/predict", response_model=PredictResponse, dependencies=[Depends(require_api_key)])
@limiter.limit(lambda: get_settings().RATE_LIMIT)
def predict(
    request: Request,  # slowapi needs the raw request to identify the client
    req: PredictRequest,
    session: Session = Depends(get_session),
    predictor: Predictor = Depends(predictor_dep),
) -> PredictResponse:
    # The predictor owns the whole serving job (predict + persist + respond);
    # the route just handles HTTP concerns: errors and metrics.
    try:
        resp = predictor.predict(req, session)
    except TimeoutError as exc:
        # Streaming mode: the consumer didn't answer in time.
        raise HTTPException(status_code=504, detail=str(exc)) from exc

    metrics.observe(resp)  # feeds the predictions_total / latency dashboards
    return resp


@app.get("/explain/linreg")
def explain_linreg() -> dict:
    """Coefficient data for the D3 bar-chart view."""
    return explain.linreg_explanation()


@app.get("/explain/lightgbm")
def explain_lightgbm(tree: int = 0) -> dict:
    """Split structure of one boosted tree for the D3 partition view."""
    return explain.lightgbm_explanation(tree_index=tree)


@app.get("/drift")
def drift_check(session: Session = Depends(get_session)) -> dict:
    """Evidently drift report: live request features vs training data."""
    return drift.run_drift_check(session)


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
