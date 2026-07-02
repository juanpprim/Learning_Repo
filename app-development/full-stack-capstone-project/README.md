# Full-Stack Capstone Project

## Objective
Ship one complete, usable application that ties together earlier tracks:
a real backend, a real frontend, and — ideally — a model or pipeline pulled
in from `mlops-production-ml/` or `data-engineering-at-scale/`.

## Suggested shape
- `backend/` — a FastAPI service (start from `../backend-api-fastapi/src/main.py`
  as a base) that exposes your core resource(s) *and* a `/predict`-style route
  backed by a model trained/tracked in `mlops-production-ml/`.
- `frontend/` — a React app (start from `../frontend-basics-react/`) that lets
  a user interact with both the CRUD resource and the model-backed endpoint.

## Example project ideas
- A small "predict and save" app: user submits input -> backend calls a model
  from `experiment-tracking-mlflow/` -> prediction is stored and shown in a history list.
- A dataset explorer: backend serves aggregates computed via
  `spark-fundamentals/` or `modern-data-stack-dbt/`, frontend renders charts/tables.
- A dashboard for the `monitoring-observability/` drift detector: backend
  exposes recent drift metrics, frontend renders them as a live-updating chart.

## Checklist
- [ ] Decide on the project idea and write a one-paragraph spec here.
- [ ] Build the backend: CRUD + at least one route that calls into another
      track's model/pipeline.
- [ ] Build the frontend: at least two connected views (list + detail, or
      dashboard + form).
- [ ] Containerize the backend with Docker (reuse patterns from
      `mlops-production-ml/model-serving-fastapi-docker/`).
- [ ] Write a short README section here documenting how to run the whole
      stack locally (`docker run` + `npm run dev`).

## Status
Not started — fill in the spec above once you've picked a direction and are
ready to build.
