"""Contract test — the response shape must be IDENTICAL in every serving mode.

Tier A ran this in `direct` mode only; Tier B added `streaming`. The SAME
assertions pass for both, which is the whole point of the SERVING_MODE flag:
the frontend and load tests never notice which path served them.
"""

import pytest

from app.schemas import PredictResponse
from tests.unit.test_schemas import VALID_FEATURES

pytestmark = pytest.mark.integration

# Each entry: (client fixture to use, expected serving_mode in the response).
MODES = [
    ("api_client", "direct"),
    ("streaming_api_client", "streaming"),
]


@pytest.mark.parametrize(("client_fixture", "mode"), MODES)
def test_response_has_exactly_the_contract_fields(request, client_fixture, mode):
    # getfixturevalue lets one test body run against differently-wired apps.
    client = request.getfixturevalue(client_fixture)

    resp = client.post("/predict", json={"features": VALID_FEATURES, "model": "lightgbm"})
    assert resp.status_code == 200

    body = resp.json()
    # Exactly the PredictResponse fields — no extras leaking, none missing.
    assert set(body.keys()) == set(PredictResponse.model_fields.keys())
    assert body["serving_mode"] == mode
