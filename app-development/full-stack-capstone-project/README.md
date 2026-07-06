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

## Streaming mode (Tier B)

Same API, different path: `/predict` → Kafka → Spark Structured Streaming →
Postgres → response. One env var flips it; the response contract is identical
(enforced by `tests/integration/test_contract.py`).

```bash
make up-streaming           # + Kafka (1 broker) + Spark consumer + Prometheus + Grafana
make train                  # (re)register models in the MLflow the Spark job reads
make run-backend-streaming  # gateway with SERVING_MODE=streaming
```

- Grafana dashboards (provisioned as code): http://localhost:3000 (admin/admin)
  — **Data-Flow / Pipeline** is the headline; run `make load` and watch it breathe.
- Prometheus: http://localhost:9090 · Spark UI: http://localhost:4040
- 3-broker replication study: `make up-streaming-3`, then
  `docker stop infra-kafka2-1` mid-load and watch the Kafka Health dashboard.
- Load comparison: `make load-sweep NAME=direct` vs `NAME=streaming`
  (see `docs/load-study.md`).

## Production depth (Tier C)

```bash
make up-full   # EVERYTHING in containers: app + Kafka + Spark + observability
make gate      # model-regression gate (CI blocks merges when a model regresses >2%)
make chaos     # kill a Kafka broker mid-flight, assert the platform survives
```

- **CI** (`.github/workflows/capstone-ci.yml`): lint → tests (testcontainers) →
  model-regression gate → image builds.
- **Drift**: `GET /drift` runs Evidently on live request features vs training
  data, exports `data_drift_share`; a provisioned Grafana alert fires above 30%.
- **Explainability**: the frontend's "Why does the model predict that?" panel —
  D3 coefficient bars (linreg) and tree partition (lightgbm) fed by
  `GET /explain/{model}`.
- **Edge**: optional API key (`API_KEY` env → `X-API-Key` header) and rate
  limiting (`RATE_LIMIT`, default 1000/minute → 429 past the limit).

## Kubernetes + HPA (Tier C.5)

Only the **stateless serving layer** moves to k8s (a local k3d cluster); the
stateful infra stays in compose. Pods reach it via `host.k3d.internal`.

```bash
make k3d-up         # cluster (needs k3d + kubectl in ~/.local/bin)
make k3d-deploy     # build + import the gateway image, apply infra/k8s/
make k3d-watch-hpa  # then run a load sweep and watch replicas rise
make k3d-chaos      # delete a pod mid-traffic; Service reroutes (20/20 served)
make k3d-down
```

Observed results (scale 1→2 at 30 users, overload lessons at 100, chaos
drill): [`docs/k8s-hpa-notes.md`](docs/k8s-hpa-notes.md). Grafana Data-Flow
panel 9 charts pod count vs RPS. *4-core host: pair with the 1-broker
overlay only.*

## Stretch (Tier D)

```bash
make amplify        # 545 rows -> 1M-row parquet (property-tested generator)
make airflow-up     # Airflow standalone orchestrating seed -> train -> gate
make airflow-check  # DAG integrity test (import errors must be empty)
make airflow-run    # trigger the pipeline; UI at http://localhost:8080
```

Implemented: D1 amplification + D2 Airflow. D3 Feast / D4 OTel / D5 GPU are
documented options — see [`docs/tier-d-notes.md`](docs/tier-d-notes.md).

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
- [x] Tier B — streaming + observability (Kafka+Spark path live, dashboards, load study)
- [x] Tier C — production depth (containers, CI + model gate, drift, D3 views, edge/chaos)
- [x] Tier C.5 — Kubernetes + HPA (k3d, probes/limits, autoscale demo, pod chaos drill)
- [ ] Tier D — stretch
