"""Tier D1: amplify the 545-row housing dataset to arbitrary size.

The real dataset is tiny on purpose (the MODEL doesn't need more), but the
SCALE tools (Spark, Airflow, warehouses) only earn their place with volume.
Sample-and-perturb: draw rows with replacement, jitter the numerics, keep
categoricals as drawn. Distributions stay realistic; size becomes whatever
you ask for.

Run:  uv run python -m ml.amplify --rows 1000000
Writes parquet to data/housing_amplified.parquet (fast, compressed, and the
natural input format for Spark/dbt experiments).
"""

import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd

from ml.dataset import load_housing_df

OUT_PATH = Path(__file__).resolve().parents[2] / "data" / "housing_amplified.parquet"

# Jitter scale per numeric column, as a fraction of the column's std.
NUMERIC_JITTER = {"area": 0.10, "price": 0.05}
# Integer columns get occasional +/-1 steps instead of gaussian noise.
INT_STEP_COLS = ["bedrooms", "bathrooms", "stories", "parking"]
INT_BOUNDS = {"bedrooms": (0, 10), "bathrooms": (0, 10), "stories": (1, 10), "parking": (0, 10)}


def amplify(df: pd.DataFrame, rows: int, seed: int = 42) -> pd.DataFrame:
    """Return `rows` synthetic rows drawn+perturbed from df. Deterministic per seed."""
    rng = np.random.default_rng(seed)
    out = df.sample(n=rows, replace=True, random_state=seed).reset_index(drop=True)

    # Continuous columns: multiplicative gaussian jitter, clipped positive.
    for col, frac in NUMERIC_JITTER.items():
        noise = rng.normal(1.0, frac, rows)
        out[col] = (out[col] * noise).clip(lower=1).round().astype(out[col].dtype)

    # Small integer columns: ~20% of rows step by +/-1, clipped to valid range.
    for col in INT_STEP_COLS:
        lo, hi = INT_BOUNDS[col]
        step = rng.choice([-1, 0, 0, 0, 1], rows)  # 40% chance of a step
        out[col] = (out[col] + step).clip(lo, hi).astype(out[col].dtype)

    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=1_000_000)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    base = load_housing_df()
    start = time.perf_counter()
    big = amplify(base, args.rows, args.seed)
    OUT_PATH.parent.mkdir(exist_ok=True)
    big.to_parquet(OUT_PATH, index=False)
    elapsed = time.perf_counter() - start

    size_mb = OUT_PATH.stat().st_size / 1e6
    print(f"amplified {len(base)} -> {args.rows:,} rows in {elapsed:.1f}s "
          f"({OUT_PATH.name}, {size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
