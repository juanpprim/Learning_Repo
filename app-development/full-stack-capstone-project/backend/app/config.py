"""App settings, read from environment variables (12-factor style).

`pydantic-settings` gives us typed env parsing for free: if SERVING_MODE is set
to anything other than "direct" or "streaming", the app refuses to start.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # The one flag that switches the serving path (see IMPLEMENTATION_SPEC.md).
    SERVING_MODE: Literal["direct", "streaming"] = "direct"

    # Where the app finds Postgres and MLflow. Defaults suit local dev
    # (docker compose exposes both on localhost).
    DATABASE_URL: str = "postgresql+psycopg2://capstone:capstone@localhost:5432/capstone"
    MLFLOW_TRACKING_URI: str = "sqlite:///mlflow.db"


@lru_cache
def get_settings() -> Settings:
    """Cached accessor so every module shares one Settings instance."""
    return Settings()
