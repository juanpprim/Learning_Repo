"""ORM tables. Two tables, one database — kept deliberately small.

- `houses`      : the batch-seeded reference/training data (written by ml/seed_data.py)
- `predictions` : every live prediction, whichever serving mode produced it
"""

from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    model: Mapped[str] = mapped_column(String(20))          # "linreg" | "lightgbm"
    serving_mode: Mapped[str] = mapped_column(String(20))   # "direct" | "streaming"
    features: Mapped[dict] = mapped_column(JSON)            # raw request features
    predicted_price: Mapped[float] = mapped_column(Float)
    latency_ms: Mapped[float] = mapped_column(Float)
