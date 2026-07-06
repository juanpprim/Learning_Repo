"""Batch seed: Housing.csv -> Postgres `houses` table. Idempotent.

Run with:  uv run python -m ml.seed_data
Re-running always leaves exactly the same 545 rows (truncate-then-insert),
which is what "idempotent" means here — no duplicates, ever.
"""

from sqlalchemy import create_engine, text

from app.config import get_settings
from ml.dataset import load_housing_df


def seed(database_url: str | None = None) -> int:
    """Load the dataset into Postgres; returns the row count written."""
    url = database_url or get_settings().DATABASE_URL
    engine = create_engine(url)
    df = load_housing_df()

    with engine.begin() as conn:  # begin() = one transaction, auto-commit/rollback
        # Idempotency: wipe and rewrite. For a static 545-row reference table
        # this is simpler and safer than upsert logic.
        conn.execute(text("DROP TABLE IF EXISTS houses"))
        df.to_sql("houses", conn, index=False)
        count = conn.execute(text("SELECT count(*) FROM houses")).scalar_one()

    print(f"seeded {count} rows into 'houses'")
    return count


if __name__ == "__main__":
    seed()
