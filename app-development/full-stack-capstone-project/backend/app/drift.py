"""Data drift check (Tier C): live prediction inputs vs the training data.

Evidently compares the distribution of each feature in recent /predict
requests against the seeded `houses` table. The share of drifted columns is
also exported as a Prometheus gauge, which is what the Grafana alert watches.

Kept as an on-demand endpoint (GET /drift) rather than a scheduled job —
simplest thing that closes the loop; Tier D's Airflow could schedule it.
"""

import pandas as pd
from prometheus_client import Gauge
from sqlalchemy import text
from sqlalchemy.orm import Session

DRIFT_SHARE = Gauge(
    "data_drift_share",
    "Share of feature columns whose live distribution drifted from training",
)

FEATURE_COLS = [
    "area", "bedrooms", "bathrooms", "stories", "mainroad", "guestroom",
    "basement", "hotwaterheating", "airconditioning", "parking", "prefarea",
    "furnishingstatus",
]
MIN_ROWS = 20  # below this, drift statistics are just noise


def _yes_no(v) -> str:
    """Normalize booleans (from request JSON) to the CSV's yes/no strings."""
    return "yes" if v in (True, "yes", "true", 1) else "no"


def run_drift_check(session: Session) -> dict:
    """Compare recent prediction features against the reference houses table."""
    reference = pd.read_sql(text("SELECT * FROM houses"), session.connection())
    reference = reference[FEATURE_COLS]

    rows = session.execute(
        text("SELECT features FROM predictions ORDER BY id DESC LIMIT 500")
    ).scalars().all()
    if len(rows) < MIN_ROWS:
        return {"status": "not_enough_data", "n_current": len(rows), "min_rows": MIN_ROWS}

    current = pd.DataFrame(list(rows))
    for col in ("mainroad", "guestroom", "basement", "hotwaterheating",
                "airconditioning", "prefarea"):
        current[col] = current[col].map(_yes_no)
    current = current[FEATURE_COLS]

    # Imported lazily: evidently is heavy and only this endpoint needs it.
    from evidently import Report
    from evidently.presets import DataDriftPreset

    report = Report([DataDriftPreset()])
    result = report.run(current_data=current, reference_data=reference).dict()

    # The preset's headline numbers live in the DriftedColumnsCount metric.
    drifted = next(
        m["value"] for m in result["metrics"] if "DriftedColumnsCount" in m["metric_name"]
    )
    share = float(drifted["share"])
    DRIFT_SHARE.set(share)  # Grafana alerts on this gauge crossing 0.3

    return {
        "status": "ok",
        "n_current": len(current),
        "drifted_columns": int(drifted["count"]),
        "drift_share": share,
    }
