"""Property-based tests for the amplifier (Tier D1) — learning goal:
hypothesis explores the input space FOR you.

Example-based tests check the cases you thought of; property tests state
invariants ("no amplified row may violate the schema") and let hypothesis
hunt for seeds/sizes that break them.
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from ml.amplify import amplify
from ml.dataset import FURNISHING, generate_synthetic

BASE = generate_synthetic(seed=1)  # module-level: built once, reused per example


@settings(max_examples=25, deadline=None)
@given(
    rows=st.integers(min_value=1, max_value=2_000),
    seed=st.integers(min_value=0, max_value=2**31 - 1),
)
def test_amplified_rows_keep_schema_invariants(rows: int, seed: int):
    big = amplify(BASE, rows, seed)

    # Size is exactly what was asked for.
    assert len(big) == rows

    # Column invariants — the same ones Pydantic enforces on live requests.
    assert (big["area"] > 0).all()
    assert (big["price"] > 0).all()
    assert big["bedrooms"].between(0, 10).all()
    assert big["bathrooms"].between(0, 10).all()
    assert big["stories"].between(1, 10).all()
    assert big["parking"].between(0, 10).all()
    assert big["furnishingstatus"].isin(FURNISHING).all()
    for col in ("mainroad", "guestroom", "basement", "hotwaterheating",
                "airconditioning", "prefarea"):
        assert big[col].isin(["yes", "no"]).all()


def test_amplify_is_deterministic_per_seed():
    a = amplify(BASE, 500, seed=7)
    b = amplify(BASE, 500, seed=7)
    assert a.equals(b)  # same seed -> byte-identical output (reproducibility)


def test_amplify_actually_perturbs():
    a = amplify(BASE, 500, seed=7)
    b = amplify(BASE, 500, seed=8)
    assert not a.equals(b)  # different seed -> different data
