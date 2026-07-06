"""Unit test for training — learning goal: pin a FLOOR on model quality.

We don't assert exact metric values (brittle); we assert the pipeline learns
*something* (r2 above a floor) on deterministic synthetic data. Tier C turns
this idea into a CI regression gate.
"""

from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from sklearn.model_selection import train_test_split

from ml.dataset import generate_synthetic
from ml.train import build_pipeline


def test_linreg_pipeline_learns_signal():
    df = generate_synthetic(seed=42)  # deterministic: same data every run
    X, y = df.drop(columns=["price"]), df["price"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    pipeline = build_pipeline(LinearRegression())
    pipeline.fit(X_train, y_train)
    r2 = r2_score(y_test, pipeline.predict(X_test))

    assert r2 > 0.5, f"model failed to learn (r2={r2:.3f})"


def test_synthetic_data_shape_matches_real_schema():
    df = generate_synthetic()
    assert len(df) == 545
    assert list(df.columns)[0] == "price"
    assert df["furnishingstatus"].isin(["furnished", "semi-furnished", "unfurnished"]).all()
