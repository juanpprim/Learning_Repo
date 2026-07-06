"""Locust load test — the Tier A baseline against `direct` mode.

Run (from backend/):
    uv run locust -f tests/load/locustfile.py --host http://localhost:8000 \
        --headless -u 100 -r 20 -t 60s --csv ../docs/load/direct-100u

Sweep -u through 10 / 100 / 1000 and keep the CSVs; Tier B re-runs the exact
same file against `streaming` mode for the comparison study.
"""

import random

from locust import HttpUser, between, task

FURNISHING = ["furnished", "semi-furnished", "unfurnished"]


def random_features() -> dict:
    """A random-but-valid house, so requests exercise the real model path."""
    return {
        "area": random.randint(1700, 16000),
        "bedrooms": random.randint(1, 6),
        "bathrooms": random.randint(1, 4),
        "stories": random.randint(1, 4),
        "mainroad": random.random() < 0.8,
        "guestroom": random.random() < 0.2,
        "basement": random.random() < 0.3,
        "hotwaterheating": random.random() < 0.1,
        "airconditioning": random.random() < 0.4,
        "parking": random.randint(0, 3),
        "prefarea": random.random() < 0.25,
        "furnishingstatus": random.choice(FURNISHING),
    }


class PredictionUser(HttpUser):
    # Small think-time so concurrency ~= active users, not a pure hammer.
    wait_time = between(0.5, 1.5)

    @task
    def predict(self):
        self.client.post(
            "/predict",
            json={
                "features": random_features(),
                # Alternate models so we get latency numbers for both.
                "model": random.choice(["linreg", "lightgbm"]),
            },
        )
