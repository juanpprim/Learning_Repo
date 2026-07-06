"""Model-regression gate (Tier C, runs in CI).

Learning goal: block a merge on MODEL quality, not just code quality.

Trains fresh candidates on the deterministic synthetic dataset and compares
their RMSE against the frozen numbers in baseline_metrics.json. Fails (exit 1)
if any model got more than TOLERANCE worse — e.g. someone "simplified" the
pipeline and silently dropped a feature.

Update the baseline INTENTIONALLY (after a justified change) with:
    uv run python -m ml.regression_gate --update-baseline
"""

import json
import sys
from pathlib import Path

from lightgbm import LGBMRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

from ml.dataset import generate_synthetic
from ml.train import build_pipeline

BASELINE_FILE = Path(__file__).with_name("baseline_metrics.json")
TOLERANCE = 0.02  # candidate may be at most 2% worse than the recorded rmse


def candidate_rmse() -> dict[str, float]:
    """Train both models on the SAME deterministic data the baseline used."""
    df = generate_synthetic(seed=42)
    X, y = df.drop(columns=["price"]), df["price"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    out = {}
    for name, est in [
        ("linreg", LinearRegression()),
        ("lightgbm", LGBMRegressor(n_estimators=200, verbose=-1)),
    ]:
        pipe = build_pipeline(est).fit(X_train, y_train)
        out[name] = float(mean_squared_error(y_test, pipe.predict(X_test)) ** 0.5)
    return out


def main() -> int:
    rmse = candidate_rmse()

    if "--update-baseline" in sys.argv:
        BASELINE_FILE.write_text(json.dumps(rmse, indent=2) + "\n")
        print(f"baseline updated: {rmse}")
        return 0

    baseline = json.loads(BASELINE_FILE.read_text())
    failed = False
    for name, base in baseline.items():
        cand = rmse[name]
        worse_by = (cand - base) / base
        status = "FAIL" if worse_by > TOLERANCE else "ok"
        if status == "FAIL":
            failed = True
        print(f"{name}: baseline rmse={base:.0f}  candidate rmse={cand:.0f} "
              f"({worse_by:+.2%})  [{status}]")

    if failed:
        print(f"\nregression gate FAILED: a model got >{TOLERANCE:.0%} worse than baseline.")
        return 1
    print("\nregression gate passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
