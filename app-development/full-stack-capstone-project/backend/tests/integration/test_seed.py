"""Integration test for the batch seed — learning goal: prove idempotency
against a REAL database, not a mock.
"""

import pytest
from sqlalchemy import create_engine, text

from ml.seed_data import seed

pytestmark = pytest.mark.integration


def count_houses(url: str) -> int:
    with create_engine(url).connect() as conn:
        return conn.execute(text("SELECT count(*) FROM houses")).scalar_one()


def test_seed_is_idempotent(postgres_url):
    # First run populates the table...
    assert seed(database_url=postgres_url) == 545
    assert count_houses(postgres_url) == 545

    # ...and a second run leaves EXACTLY the same rows (no duplicates).
    assert seed(database_url=postgres_url) == 545
    assert count_houses(postgres_url) == 545
