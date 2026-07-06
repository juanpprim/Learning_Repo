"""Loading (or generating) the housing dataset.

Preferred source is the real Kaggle CSV at data/Housing.csv (see README).
If it's missing we generate a deterministic synthetic stand-in with the same
schema and plausible price/feature relationships, so the whole project stays
runnable without Kaggle credentials.
"""

from pathlib import Path

import numpy as np
import pandas as pd

# data/ lives at the project root, two levels above backend/ml/
DATA_CSV = Path(__file__).resolve().parents[2] / "data" / "Housing.csv"

CATEGORICAL_YESNO = [
    "mainroad",
    "guestroom",
    "basement",
    "hotwaterheating",
    "airconditioning",
    "prefarea",
]
FURNISHING = ["furnished", "semi-furnished", "unfurnished"]
N_ROWS = 545  # same size as the real dataset


def generate_synthetic(n: int = N_ROWS, seed: int = 42) -> pd.DataFrame:
    """Fabricate n rows with a real price signal (so models can learn r2 > 0.5)."""
    rng = np.random.default_rng(seed)
    df = pd.DataFrame(
        {
            "area": rng.integers(1650, 16200, n),
            "bedrooms": rng.integers(1, 7, n),
            "bathrooms": rng.integers(1, 5, n),
            "stories": rng.integers(1, 5, n),
            "parking": rng.integers(0, 4, n),
            "furnishingstatus": rng.choice(FURNISHING, n),
        }
    )
    for col in CATEGORICAL_YESNO:
        df[col] = rng.choice(["yes", "no"], n, p=[0.3, 0.7])

    # Price = linear mix of features + noise. Coefficients are arbitrary but
    # produce prices in the same ballpark as the real data (~1.7M-13M rupees).
    price = (
        350 * df["area"]
        + 250_000 * df["bedrooms"]
        + 400_000 * df["bathrooms"]
        + 300_000 * df["stories"]
        + 150_000 * df["parking"]
        + 200_000 * (df["airconditioning"] == "yes")
        + 150_000 * (df["prefarea"] == "yes")
        + rng.normal(0, 300_000, n)
    )
    df["price"] = price.clip(lower=100_000).round().astype(int)
    # Match the real CSV's column order (price first).
    ordered = [
        "price", "area", "bedrooms", "bathrooms", "stories",
        "mainroad", "guestroom", "basement", "hotwaterheating",
        "airconditioning", "parking", "prefarea", "furnishingstatus",
    ]
    return df[ordered]


def load_housing_df() -> pd.DataFrame:
    """Real CSV if present, synthetic otherwise."""
    if DATA_CSV.exists():
        return pd.read_csv(DATA_CSV)
    print(f"NOTE: {DATA_CSV} not found - using deterministic synthetic data.")
    return generate_synthetic()
