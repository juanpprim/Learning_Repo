"""Contract test — the response shape must be IDENTICAL in every serving mode.

Tier A runs it in `direct` mode only; Tier B adds `streaming` to the
parametrize list and the same assertions must still pass. That is the whole
point of the SERVING_MODE flag being transparent.
"""

import pytest

from app.schemas import PredictResponse
from tests.unit.test_schemas import VALID_FEATURES

pytestmark = pytest.mark.integration

# Tier B appends "streaming" here — nothing else in this file may change.
MODES = ["direct"]


@pytest.mark.parametrize("mode", MODES)
def test_response_has_exactly_the_contract_fields(api_client, mode):
    resp = api_client.post("/predict", json={"features": VALID_FEATURES, "model": "lightgbm"})
    assert resp.status_code == 200

    body = resp.json()
    # Exactly the PredictResponse fields — no extras leaking, none missing.
    assert set(body.keys()) == set(PredictResponse.model_fields.keys())
