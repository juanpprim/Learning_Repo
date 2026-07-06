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

    columns = list(df.columns)
    ddl = ", ".join(
        f"{c} TEXT" if df[c].dtype == object else f"{c} BIGINT" for c in columns
    )
    insert = text(
        f"INSERT INTO houses ({', '.join(columns)}) "
        f"VALUES ({', '.join(':' + c for c in columns)})"
    )

    # Idempotency: wipe and rewrite in ONE transaction. Plain SQL instead of
    # pandas.to_sql so this also runs inside the Airflow image, which pins
    # SQLAlchemy 1.4 (pandas' to_sql needs 2.x).
    with engine.begin() as conn:
        conn.execute(text("DROP TABLE IF EXISTS houses"))
        conn.execute(text(f"CREATE TABLE houses ({ddl})"))
        conn.execute(insert, df.to_dict("records"))  # executemany under the hood
        count = conn.execute(text("SELECT count(*) FROM houses")).scalar_one()

    print(f"seeded {count} rows into 'houses'")
    return count


if __name__ == "__main__":
    seed()
