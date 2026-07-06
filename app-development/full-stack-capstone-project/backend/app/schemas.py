"""The API contract — request/response models shared by BOTH serving modes.

This file is deliberately boring and frozen: `direct` and `streaming` modes,
the frontend, and the load tests all depend on these exact shapes.
"""

from typing import Literal

import pandas as pd
from pydantic import BaseModel, Field


class HouseFeatures(BaseModel):
    """The 12 features of the Kaggle housing dataset, with validated ranges."""

    area: int = Field(gt=0, description="Plot area in square feet")
    bedrooms: int = Field(ge=0, le=10)
    bathrooms: int = Field(ge=0, le=10)
    stories: int = Field(ge=1, le=10)
    mainroad: bool
    guestroom: bool
    basement: bool
    hotwaterheating: bool
    airconditioning: bool
    parking: int = Field(ge=0, le=10)
    prefarea: bool
    furnishingstatus: Literal["furnished", "semi-furnished", "unfurnished"]

    def to_frame(self) -> pd.DataFrame:
        """Convert to a one-row DataFrame matching the TRAINING data format.

        The CSV encodes booleans as "yes"/"no" strings, so the model pipeline
        expects those — we translate our typed bools back here, in one place.
        """
        row = self.model_dump()
        for col in (
            "mainroad",
            "guestroom",
            "basement",
            "hotwaterheating",
            "airconditioning",
            "prefarea",
        ):
            row[col] = "yes" if row[col] else "no"
        return pd.DataFrame([row])


class PredictRequest(BaseModel):
    features: HouseFeatures
    # Which registered MLflow model to use; anything else is a 422.
    model: Literal["linreg", "lightgbm"] = "lightgbm"


class PredictResponse(BaseModel):
    prediction_id: int
    predicted_price: float
    model: str
    serving_mode: str
    latency_ms: float


class PredictionRecord(BaseModel):
    """One row of the history list (GET /predictions)."""

    id: int
    created_at: str
    model: str
    serving_mode: str
    features: dict
    predicted_price: float
    latency_ms: float
