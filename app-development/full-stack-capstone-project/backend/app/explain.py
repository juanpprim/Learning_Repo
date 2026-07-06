"""Model explainability data for the D3 frontend views (Tier C).

Two very different explanation shapes, matching the two model families:
- linreg   -> coefficients (a linear model IS its coefficients)
- lightgbm -> the split structure of a tree (feature-space partition, r2d3-style)

We load the raw sklearn Pipeline (not the pyfunc wrapper) because we need the
fitted estimator's internals, which pyfunc deliberately hides.
"""

from functools import lru_cache

import mlflow.sklearn

from app.config import get_settings


@lru_cache(maxsize=2)
def _load_pipeline(name: str):
    """The full sklearn Pipeline (preprocess + model) behind an alias."""
    mlflow.set_tracking_uri(get_settings().MLFLOW_TRACKING_URI)
    return mlflow.sklearn.load_model(f"models:/{name}@production")


def linreg_explanation() -> dict:
    """Coefficients on the one-hot-expanded features, sorted by |impact|."""
    pipeline = _load_pipeline("linreg")
    names = pipeline.named_steps["preprocess"].get_feature_names_out()
    model = pipeline.named_steps["model"]

    coefficients = [
        # strip the ColumnTransformer prefixes ("onehot__", "remainder__")
        {"feature": n.split("__", 1)[-1], "coefficient": float(c)}
        for n, c in zip(names, model.coef_)
    ]
    coefficients.sort(key=lambda d: abs(d["coefficient"]), reverse=True)
    return {"intercept": float(model.intercept_), "coefficients": coefficients}


def _simplify_node(node: dict, feature_names: list[str]) -> dict:
    """Recursively convert LightGBM's verbose node dump into what D3 needs."""
    if "leaf_value" in node:  # terminal node: just the predicted value
        return {"value": float(node["leaf_value"])}
    return {
        "feature": feature_names[node["split_feature"]],
        "threshold": float(node["threshold"]),
        "left": _simplify_node(node["left_child"], feature_names),
        "right": _simplify_node(node["right_child"], feature_names),
    }


def lightgbm_explanation(tree_index: int = 0) -> dict:
    """The split structure of one tree — the recursive feature-space partition."""
    pipeline = _load_pipeline("lightgbm")
    booster = pipeline.named_steps["model"].booster_
    dump = booster.dump_model()

    # The booster only saw a bare numpy array ("Column_15"), so recover real
    # names from the preprocessor: transformed column i == its i-th output.
    names = [
        n.split("__", 1)[-1]
        for n in pipeline.named_steps["preprocess"].get_feature_names_out()
    ]
    tree_index = max(0, min(tree_index, len(dump["tree_info"]) - 1))
    tree = dump["tree_info"][tree_index]["tree_structure"]

    return {
        "tree_index": tree_index,
        "n_trees": len(dump["tree_info"]),
        "tree": _simplify_node(tree, names),
    }
