"""Unit tests for the API contract — learning goal: validation is code.

No I/O here: we only prove that Pydantic accepts good payloads and rejects bad
ones, so bad input can never reach a model.
"""

import pytest
from pydantic import ValidationError

from app.schemas import HouseFeatures, PredictRequest

VALID_FEATURES = {
    "area": 7420,
    "bedrooms": 4,
    "bathrooms": 2,
    "stories": 3,
    "mainroad": True,
    "guestroom": False,
    "basement": False,
    "hotwaterheating": False,
    "airconditioning": True,
    "parking": 2,
    "prefarea": True,
    "furnishingstatus": "furnished",
}


def test_valid_payload_parses():
    req = PredictRequest(features=VALID_FEATURES, model="linreg")
    assert req.features.area == 7420
    assert req.model == "linreg"


def test_default_model_is_lightgbm():
    assert PredictRequest(features=VALID_FEATURES).model == "lightgbm"


def test_negative_bedrooms_rejected():
    bad = {**VALID_FEATURES, "bedrooms": -1}
    with pytest.raises(ValidationError):
        HouseFeatures(**bad)


def test_unknown_model_rejected():
    with pytest.raises(ValidationError):
        PredictRequest(features=VALID_FEATURES, model="xgboost")


def test_furnishingstatus_outside_enum_rejected():
    bad = {**VALID_FEATURES, "furnishingstatus": "palace"}
    with pytest.raises(ValidationError):
        HouseFeatures(**bad)


def test_to_frame_converts_bools_to_yes_no():
    # The model pipeline was trained on "yes"/"no" strings, so the conversion
    # in to_frame() is part of the contract too.
    frame = HouseFeatures(**VALID_FEATURES).to_frame()
    assert frame.loc[0, "mainroad"] == "yes"
    assert frame.loc[0, "guestroom"] == "no"
    assert frame.shape == (1, 12)
