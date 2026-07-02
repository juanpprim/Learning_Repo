# Experiment Tracking with MLflow

## Objectives
- Understand why ad-hoc notebook experiment tracking (renamed CSVs, commented-out
  hyperparameters) breaks down and what a tracking system replaces.
- Log params, metrics, and artifacts for training runs with MLflow Tracking.
- Compare runs in the MLflow UI and pick a best model by metric.
- Register a model version in the MLflow Model Registry and move it through
  stages (`Staging` -> `Production`).

## Key concepts
- Tracking server vs. local file store (`mlruns/`) vs. remote backend (Postgres + S3/GCS).
- Runs, experiments, params, metrics, tags, artifacts.
- Autologging (`mlflow.sklearn.autolog()`, `mlflow.pytorch.autolog()`) vs. manual logging.
- Model Registry: versions, stages, aliases.

## Resources
- MLflow docs — Tracking: https://mlflow.org/docs/latest/tracking.html
- MLflow docs — Model Registry: https://mlflow.org/docs/latest/model-registry.html
- "Made With ML" MLOps course (experiment tracking section): https://madewithml.com/

## Checklist
- [ ] Run `mlflow ui` locally and confirm the tracking UI loads.
- [ ] Log at least 3 runs of a simple model (e.g. scikit-learn classifier) with
      different hyperparameters, using manual `mlflow.log_param` / `log_metric`.
- [ ] Repeat using `autolog()` and compare what gets captured automatically.
- [ ] Log a model artifact and reload it with `mlflow.pyfunc.load_model`.
- [ ] Register the best run's model in the Model Registry and transition it to
      `Staging`.

## Mini-project
Train 3-5 variants of a model on a small dataset (e.g. `sklearn.datasets`),
track every run in MLflow, and produce a short comparison (in the notebook)
of which run wins and why — then register that model version.
