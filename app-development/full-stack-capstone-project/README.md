# Full-Stack Capstone — Real-Time ML Platform

> **Deep dive:** open [`key_concepts.html`](key_concepts.html) in a browser for animated explanations of the underlying concepts.

House-price prediction platform tying the Learning Repo tracks together:
FastAPI + MLflow + Postgres + React (Tier A), Kafka + Spark + Prometheus/Grafana
(Tier B), CI/drift/chaos hardening (Tier C), and stretch tooling (Tier D).

- **What & why:** [`PROJECT_PLAN.md`](PROJECT_PLAN.md)
- **How (build order, contracts, tests):** [`IMPLEMENTATION_SPEC.md`](IMPLEMENTATION_SPEC.md)
- **Deferred ideas:** [`FUTURE_IMPROVEMENTS.md`](FUTURE_IMPROVEMENTS.md)

## Quickstart (Tier A, `direct` mode)

Prereqs: Docker, [uv](https://docs.astral.sh/uv/), Node 20+.

```bash
make install     # backend (uv sync) + frontend (npm install)
make up          # Postgres + MLflow UI (http://localhost:5000)
make seed        # Housing.csv -> Postgres  (synthetic fallback, see below)
make train       # LinReg + LightGBM -> MLflow registry (@production)
make run-backend # FastAPI on http://localhost:8000  (docs at /docs)
make run-frontend# React on http://localhost:5173
```

### Dataset

Real data: download [Kaggle housing-prices-dataset](https://www.kaggle.com/datasets/yasserh/housing-prices-dataset)
and place it at `data/Housing.csv`. If the file is absent, `make seed` and
`make train` fall back to a **deterministic synthetic dataset** with the same
schema and a real price signal, so everything stays runnable offline.

## Tests

```bash
make test-unit   # fast: schemas, predictor logic, training floor (no Docker)
make test        # + integration: real Postgres via testcontainers
cd frontend && npm test           # Vitest component tests
cd frontend && npm run test:e2e   # Playwright (needs backend running)
make load        # Locust baseline -> docs/load/ (see docs/load-baseline.md)
```

## Layout

```
backend/   FastAPI app (app/), ML scripts (ml/), tests (tests/)
frontend/  React + Vite + TS (src/), Vitest + Playwright (tests/)
infra/     docker-compose files (base now; Kafka/observability overlays in Tier B)
docs/      load-test results and study write-ups
```

## Status

- [x] Tier A — core walking skeleton (direct mode, e2e tested, load baseline)
- [ ] Tier B — streaming + observability
- [ ] Tier C — production depth
- [ ] Tier D — stretch
