# Full-Stack Capstone — Real-Time ML Platform

> **Deep dive:** open [`key_concepts.html`](key_concepts.html) in a browser for animated explanations of the underlying concepts.

House-price prediction platform tying the Learning Repo tracks together:
FastAPI + MLflow + Postgres + React (Tier A), Kafka + Spark + Prometheus/Grafana
(Tier B), CI/drift/chaos hardening (Tier C), Kubernetes + HPA (Tier C.5),
and stretch tooling (Tier D).

- **What & why:** [`PROJECT_PLAN.md`](PROJECT_PLAN.md)
- **How (build order, contracts, tests):** [`IMPLEMENTATION_SPEC.md`](IMPLEMENTATION_SPEC.md)
- **What was learned building it:** [`docs/LEARNINGS.md`](docs/LEARNINGS.md)
- **Deferred ideas + review backlog:** [`FUTURE_IMPROVEMENTS.md`](FUTURE_IMPROVEMENTS.md)

## Prerequisites

- Docker (with the compose plugin), [uv](https://docs.astral.sh/uv/), Node 20+
- Tier C.5 only: `k3d` + `kubectl` in `~/.local/bin`
- One-time setup: `make install` (backend `uv sync` + frontend `npm install`)

Every routine action is a `make` target — run `make <target>` from this
directory. The tiers stack: each one assumes the previous tier's setup
(models trained, etc.) has happened at least once.

---

## Running the tiers

### Tier A — core walking skeleton (`direct` mode)

The whole product with the simplest serving path: model called in-process.

```bash
make up            # 1. Postgres + MLflow UI (http://localhost:5000)
make seed          # 2. Housing.csv -> Postgres (synthetic fallback, see Dataset)
make train         # 3. LinReg + LightGBM -> MLflow registry (@production)
make run-backend   # 4. FastAPI on http://localhost:8000 (docs at /docs)
make run-frontend  # 5. React on http://localhost:5173 — predict + history
make load          # optional: Locust baseline -> docs/load/ (docs/load-baseline.md)
make down          # stop containers (data volumes survive)
```

### Tier B — streaming + observability

Same API, different path: `/predict` → Kafka → Spark → Postgres → response.
One env var flips it; the response contract is identical (enforced by
`tests/integration/test_contract.py`).

```bash
make up-streaming           # 1. + Kafka (1 broker) + Spark consumer + Prometheus + Grafana
make train                  # 2. only if models aren't in this MLflow yet
make run-backend-streaming  # 3. gateway with SERVING_MODE=streaming
make load-sweep NAME=streaming   # 4. sweep; compare vs NAME=direct (docs/load-study.md)
make down-streaming         # stop the whole streaming stack
```

Watch it live: Grafana http://localhost:3000 (admin/admin) → **Data-Flow /
Pipeline** dashboard; Prometheus :9090; Spark UI :4040.

Replication study (3 brokers, rf=3): `make up-streaming-3`, then
`docker stop infra-kafka2-1` mid-load and watch the **Kafka Health**
dashboard (write-up: `docs/kafka-3broker-notes.md`).

### Tier C — production depth

```bash
make up-full    # EVERYTHING in containers: app + Kafka + Spark + observability
make gate       # model-regression gate (same command CI runs; fails on >2% RMSE regression)
make chaos      # kill a Kafka broker mid-flight (needs up-streaming-3 running)
make down-full  # stop the full containerized stack
```

- **CI** (`.github/workflows/capstone-ci.yml`): lint → tests (testcontainers) →
  model-regression gate → image builds.
- **Drift**: `curl localhost:8000/drift` runs Evidently on live request
  features vs training data; a provisioned Grafana alert fires above 30%.
- **Explainability**: the frontend's "Why does the model predict that?" panel
  (D3 coefficient bars + tree partition, fed by `GET /explain/{model}`).
- **Edge**: optional API key (`API_KEY` env → `X-API-Key` header) and rate
  limiting (`RATE_LIMIT`, default 1000/minute → 429 past the limit).

### Tier C.5 — Kubernetes + HPA (k3d)

Only the **stateless serving layer** moves to k8s; the stateful infra stays in
compose (pods reach it via `host.k3d.internal`). Run alongside the
**1-broker** overlay only — the host has 4 cores.

```bash
make up-streaming   # 1. the compose stack the pods depend on
make k3d-up         # 2. local cluster (gateway on :8000, kube-state-metrics on :30080)
make k3d-deploy     # 3. build + import the gateway image, apply infra/k8s/
make k3d-watch-hpa  # 4. in one terminal…
make load-sweep NAME=k8s   # …while a sweep runs in another: replicas rise, then drain
make k3d-chaos      # 5. delete a pod mid-traffic; Service reroutes (20/20 served)
make k3d-status     # pods / HPA / ingress at a glance
make k3d-down       # delete the cluster (compose stack untouched)
```

Observed results (scale 1→2 at 30 users, overload lessons at 100, chaos
drill): [`docs/k8s-hpa-notes.md`](docs/k8s-hpa-notes.md). Grafana Data-Flow
panel 9 charts pod count vs RPS.

### Tier D — stretch (à la carte)

```bash
make amplify        # D1: 545 rows -> 1M-row parquet (property-tested generator)
make airflow-up     # D2: Airflow standalone orchestrating seed -> train -> gate
make airflow-check  #     DAG integrity test (import errors must be empty)
make airflow-run    #     unpause + trigger the pipeline; UI at http://localhost:8080
```

Implemented: D1 amplification + D2 Airflow. D3 Feast / D4 OTel / D5 GPU are
documented options — see [`docs/tier-d-notes.md`](docs/tier-d-notes.md).

---

## Dataset

Real data: download the [Kaggle housing-prices-dataset](https://www.kaggle.com/datasets/yasserh/housing-prices-dataset)
and place it at `data/Housing.csv`. If the file is absent, `make seed` and
`make train` fall back to a **deterministic synthetic dataset** with the same
schema and a real price signal, so everything stays runnable offline.

## Tests

```bash
make test-unit   # fast: schemas, predictor logic, training floor, amplifier (no Docker)
make test        # + integration: real Postgres/Kafka via testcontainers
cd frontend && npm test           # Vitest component tests (incl. D3 views)
cd frontend && npm run test:e2e   # Playwright (needs Tier A stack running)
make gate        # model-regression gate
```

## Layout

```
backend/   FastAPI app (app/), ML scripts (ml/), Spark job (spark/),
           Airflow DAG (airflow_dags/), tests (tests/)
frontend/  React + Vite + TS (src/), Vitest + Playwright (tests/)
infra/     docker-compose files + overlays, k8s manifests (k8s/),
           Prometheus + Grafana provisioning
docs/      learnings, load studies, kafka/k8s notes
```

## Status

- [x] Tier A — core walking skeleton (direct mode, e2e tested, load baseline)
- [x] Tier B — streaming + observability (Kafka+Spark path live, dashboards, load study)
- [x] Tier C — production depth (containers, CI + model gate, drift, D3 views, edge/chaos)
- [x] Tier C.5 — Kubernetes + HPA (k3d, probes/limits, autoscale demo, pod chaos drill)
- [x] Tier D — stretch (D1 amplification + D2 Airflow; D3/D4/D5 documented options)
