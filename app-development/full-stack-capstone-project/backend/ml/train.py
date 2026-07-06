"""Train LinearRegression + LightGBM, log to MLflow, register @production.

Run with:  uv run python -m ml.train
Both models are one sklearn Pipeline each (preprocessing + estimator), so the
serving side never has to re-implement preprocessing — it just calls .predict()
on raw request rows.
"""

import mlflow
import pandas as pd
from lightgbm import LGBMRegressor
from mlflow.models import infer_signature
from mlflow.tracking import MlflowClient
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from app.config import get_settings
from ml.dataset import CATEGORICAL_YESNO, load_housing_df

# All string columns get one-hot encoded; numerics pass through untouched.
CATEGORICAL = CATEGORICAL_YESNO + ["furnishingstatus"]


def build_pipeline(estimator) -> Pipeline:
    preprocess = ColumnTransformer(
        transformers=[("onehot", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL)],
        remainder="passthrough",  # numeric columns flow through as-is
    )
    return Pipeline([("preprocess", preprocess), ("model", estimator)])


def train_one(name: str, estimator, X_train, X_test, y_train, y_test) -> dict:
    """Train one model, log it to MLflow, register it, alias it @production."""
    pipeline = build_pipeline(estimator)

    with mlflow.start_run(run_name=name):
        pipeline.fit(X_train, y_train)
        preds = pipeline.predict(X_test)

        # The three regression metrics we care about; rmse is the CI gate metric.
        metrics = {
            "rmse": float(mean_squared_error(y_test, preds) ** 0.5),
            "mae": float(mean_absolute_error(y_test, preds)),
            "r2": float(r2_score(y_test, preds)),
        }
        mlflow.log_metrics(metrics)

        # Log + register in one call; signature records the input schema.
        # skops_trusted_types: MLflow's safe serializer must be told that the
        # LightGBM classes inside the pipeline are OK to load back.
        signature = infer_signature(X_train, preds)
        info = mlflow.sklearn.log_model(
            pipeline,
            name=name,
            signature=signature,
            registered_model_name=name,
            skops_trusted_types=[
                "collections.OrderedDict",
                "lightgbm.basic.Booster",
                "lightgbm.sklearn.LGBMRegressor",
            ],
        )

    # Point the @production alias at the version we just registered, so serving
    # code can always load "models:/<name>@production" without knowing versions.
    client = MlflowClient()
    client.set_registered_model_alias(name, "production", info.registered_model_version)

    print(f"{name}: {metrics} -> registered v{info.registered_model_version} @production")
    return metrics


def train_all(df: pd.DataFrame | None = None) -> dict[str, dict]:
    """Train both models; returns {model_name: metrics}. Reused by tests/CI."""
    mlflow.set_tracking_uri(get_settings().MLFLOW_TRACKING_URI)
    mlflow.set_experiment("housing")

    if df is None:
        df = load_housing_df()
    X = df.drop(columns=["price"])
    y = df["price"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    return {
        "linreg": train_one("linreg", LinearRegression(), X_train, X_test, y_train, y_test),
        # verbose=-1 silences LightGBM's per-iteration chatter.
        "lightgbm": train_one(
            "lightgbm", LGBMRegressor(n_estimators=200, verbose=-1),
            X_train, X_test, y_train, y_test,
        ),
    }


if __name__ == "__main__":
    train_all()
