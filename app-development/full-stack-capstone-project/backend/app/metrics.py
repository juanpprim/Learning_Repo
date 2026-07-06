"""Custom Prometheus metrics, labeled by model and serving_mode.

The instrumentator in main.py already gives generic per-route HTTP metrics;
these two are the DOMAIN metrics the Grafana dashboards are built on.
"""

from prometheus_client import Counter, Histogram

from app.schemas import PredictResponse

PREDICTIONS = Counter(
    "predictions_total",
    "Predictions served",
    labelnames=["model", "serving_mode"],
)

# Buckets span sub-ms direct calls up to multi-second queued round trips.
LATENCY = Histogram(
    "prediction_latency_seconds",
    "End-to-end /predict latency",
    labelnames=["model", "serving_mode"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10],
)


def observe(resp: PredictResponse) -> None:
    """Record one served prediction (called from the /predict route)."""
    PREDICTIONS.labels(resp.model, resp.serving_mode).inc()
    LATENCY.labels(resp.model, resp.serving_mode).observe(resp.latency_ms / 1000)
