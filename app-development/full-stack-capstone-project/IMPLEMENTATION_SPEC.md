# Implementation Spec — Real-Time ML Platform

> Companion to [`PROJECT_PLAN.md`](PROJECT_PLAN.md). The plan says *what and why*;
> this doc says *how* — concrete files, contracts, build order, and the tests to
> write at each step. Guiding rule: **keep every piece the simplest thing that
> teaches the concept.** No abstraction earns its place until a tier needs it.

---

## How to use this spec

- Build **top to bottom, tier by tier**. Each tier ends in something you can run
  and demo. Don't start Tier B until Tier A's tests are green.
- Every task has a ✅ **Definition of Done** and, where useful, a 🧪 **Test**
  block. Tests are chosen for *learning value*, not coverage percentage — each
  one demonstrates a different testing style (unit, integration, e2e, load).
- Copy the file tree exactly; later tiers assume these paths.

### Testing philosophy (the learning goal)

| Test type | What it proves | Tool | First appears |
|-----------|----------------|------|---------------|
| **Unit** | one function does its job, no I/O | pytest | Tier A |
| **Integration** | two real components talk (API↔DB, API↔model) | pytest + TestClient + testcontainers | Tier A |
| **Contract** | request/response schema is stable across modes | pytest + Pydantic | Tier A |
| **End-to-end** | a user action works through the whole stack | Playwright | Tier A→B |
| **Load** | system behaves under concurrency | Locust | Tier A |
| **Streaming/async** | Kafka→Spark path produces a result | pytest + testcontainers-kafka | Tier B |
| **Chaos** | system recovers from a killed component | shell + Grafana assertion | Tier C |
| **Regression (model)** | new model isn't worse than champion | pytest gate in CI | Tier C |

Keep the **test pyramid**: many unit, fewer integration, a handful of e2e, one
load scenario per mode. Don't invert it.

---

## Repository layout (target end-state)

Build this incrementally — create a folder only when its tier arrives.

```
full-stack-capstone-project/
├── backend/
│   ├── app/
│   │   ├── main.py                # FastAPI app factory + routes
│   │   ├── config.py              # env settings (SERVING_MODE, DB URL, ...)
│   │   ├── schemas.py             # Pydantic request/response models (the CONTRACT)
│   │   ├── db.py                  # SQLAlchemy engine/session
│   │   ├── models_orm.py          # Prediction table
│   │   ├── serving/
│   │   │   ├── base.py            # Predictor protocol (interface)
│   │   │   ├── direct.py          # in-process MLflow model call
│   │   │   └── streaming.py       # Kafka producer + result poll/SSE   (Tier B)
│   │   └── metrics.py             # prometheus instrumentator wiring    (Tier B)
│   ├── ml/
│   │   ├── seed_data.py           # Housing.csv -> Postgres (idempotent)
│   │   └── train.py               # LinReg + LightGBM -> MLflow
│   ├── spark/
│   │   └── consumer.py            # Structured Streaming job            (Tier B)
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── load/locustfile.py
│   ├── pyproject.toml             # deps + ruff + pytest config
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── api.ts                 # typed fetch client
│   │   ├── components/
│   │   │   ├── PredictForm.tsx
│   │   │   ├── HistoryList.tsx
│   │   │   └── explain/           # D3 views                            (Tier C)
│   │   └── main.tsx
│   ├── tests/                     # Vitest unit + Playwright e2e
│   ├── package.json
│   └── Dockerfile
├── infra/
│   ├── docker-compose.yml               # base: postgres, mlflow, backend, frontend
│   ├── docker-compose.kafka-1broker.yml # Tier B overlay
│   ├── docker-compose.kafka-3broker.yml # Tier B overlay
│   ├── docker-compose.observability.yml # Tier B overlay (prom+grafana+exporters)
│   ├── prometheus/prometheus.yml
│   └── grafana/provisioning/             # dashboards + datasources as code
├── data/Housing.csv
├── .github/workflows/ci.yml             # Tier C
└── Makefile                             # one-liners for every common task
```

**Simplicity guardrails**
- One Postgres instance serves both reference data *and* the result store (two
  tables, not two databases).
- One MLflow instance, file-backed store + local artifacts — no S3/minio until
  it's actually needed.
- The `Predictor` protocol (`serving/base.py`) is the *only* seam between direct
  and streaming modes. Everything else stays identical — that's what keeps the
  contract test meaningful.

---

# Tier A — Core walking skeleton

**Goal:** a user opens the web app, submits house features, picks a model, gets a
price back, and sees it in a history list — all in `direct` mode. Plus a Locust
baseline. This alone satisfies the full brief end-to-end.

**Stack:** Postgres · MLflow (local) · FastAPI · React · Locust. No Kafka, no Spark.

### A1 — Project scaffolding & tooling

- `backend/pyproject.toml`: deps `fastapi`, `uvicorn[standard]`, `pydantic-settings`,
  `sqlalchemy`, `psycopg2-binary`, `scikit-learn`, `lightgbm`, `mlflow`, `pandas`;
  dev deps `pytest`, `httpx`, `ruff`, `testcontainers[postgres]`, `locust`.
- Configure `ruff` and `pytest` in `pyproject.toml` (no separate config files).
- `Makefile` targets: `install`, `seed`, `train`, `run-backend`, `run-frontend`,
  `test`, `lint`, `load`.

✅ **Done:** `make install && make lint` runs clean on an empty project.

### A2 — Config & the contract (`config.py`, `schemas.py`)

`config.py` — `pydantic-settings.BaseSettings`:
```
SERVING_MODE: Literal["direct", "streaming"] = "direct"
DATABASE_URL: str
MLFLOW_TRACKING_URI: str
```

`schemas.py` — this is the **frozen contract** used by both modes and the frontend:
```
class HouseFeatures(BaseModel):   # 12 fields from the dataset, validated ranges
    area: int; bedrooms: int; bathrooms: int; stories: int
    mainroad: bool; guestroom: bool; basement: bool; hotwaterheating: bool
    airconditioning: bool; parking: int; prefarea: bool
    furnishingstatus: Literal["furnished","semi-furnished","unfurnished"]

class PredictRequest(BaseModel):
    features: HouseFeatures
    model: Literal["linreg", "lightgbm"] = "lightgbm"

class PredictResponse(BaseModel):
    prediction_id: int
    predicted_price: float
    model: str
    serving_mode: str
    latency_ms: float
```

🧪 **Unit test** (`tests/unit/test_schemas.py`) — *learning: validation is code.*
- valid payload parses; `bedrooms: -1` raises `ValidationError`; unknown
  `model: "xgboost"` is rejected; `furnishingstatus` outside the enum is rejected.

### A3 — Data seed (`ml/seed_data.py`)

- Download instructions in README (Kaggle `yasserh/housing-prices-dataset` →
  `data/Housing.csv`). Script reads CSV → writes to `houses` table.
- **Idempotent:** `CREATE TABLE IF NOT EXISTS`; truncate-then-insert, or upsert on
  a synthetic row id. Re-running yields the same 545 rows, no duplicates.

🧪 **Integration test** (`tests/integration/test_seed.py`) — *learning:
testcontainers spins a real Postgres in Docker; no mocks.*
- start Postgres container → run seed → assert `SELECT count(*) == 545` → run seed
  **again** → assert still 545 (proves idempotency).

### A4 — Training (`ml/train.py`)

- Load from Postgres (or CSV fallback), split train/test, build a **single sklearn
  `Pipeline`** per model: `ColumnTransformer` (one-hot the categoricals) →
  estimator. Two estimators: `LinearRegression`, `LGBMRegressor`.
- Log to MLflow: params, `rmse` + `mae` + `r2` on holdout, and the model artifact.
- Register both under names `linreg` / `lightgbm`, promote to alias `@production`.

✅ **Done:** `make train` produces two registered models loadable by
`mlflow.pyfunc.load_model("models:/lightgbm@production")`.

🧪 **Unit test** (`tests/unit/test_train.py`) — *learning: pin model quality.*
- train on a tiny fixed slice with a fixed seed → assert `r2 > 0.5` (a floor, not
  a brittle exact value). This is the seed of the Tier C regression gate.

### A5 — Serving seam (`serving/base.py`, `serving/direct.py`)

`base.py`:
```
class Predictor(Protocol):
    def predict(self, req: PredictRequest) -> PredictResponse: ...
```

`direct.py` — `DirectPredictor`: lazy-load both MLflow models into a dict, call
`.predict()` on the chosen one, time it, return `PredictResponse`. A factory
`get_predictor(settings)` returns the right implementation based on `SERVING_MODE`
(streaming raises `NotImplementedError` until Tier B).

🧪 **Unit test** (`tests/unit/test_direct_predictor.py`) — *learning: mock the
boundary, test the logic.*
- inject a fake model whose `.predict()` returns `[42.0]` → assert the predictor
  fills `predicted_price=42.0`, sets `serving_mode="direct"`, and `latency_ms > 0`.

### A6 — API (`main.py`, `db.py`, `models_orm.py`)

Routes:
- `POST /predict` → validate, call predictor, **persist** the prediction to a
  `predictions` table, return `PredictResponse`.
- `GET /predictions?limit=20` → recent history (for the frontend list).
- `GET /health` → `{"status":"ok"}`.
- `GET /metrics` → wired in Tier B (leave a stub or add the instrumentator now).

`predictions` table: id, created_at, model, serving_mode, features (JSONB),
predicted_price, latency_ms.

🧪 **Integration test** (`tests/integration/test_api.py`) — *learning: FastAPI
`TestClient` + real DB + a stubbed model = the sweet spot.*
- `POST /predict` with a valid body → `200`, response matches `PredictResponse`
  schema, and a row now exists in `predictions`.
- `GET /predictions` returns that row.
- `POST /predict` with `bedrooms: -1` → `422` (FastAPI validation).

🧪 **Contract test** (`tests/integration/test_contract.py`) — *learning: the flag
must not change the API.* Parametrize the same request; in `direct` mode assert
the response has exactly the `PredictResponse` fields. (In Tier B, extend this
same test to run in `streaming` mode — the payoff of writing it now.)

### A7 — Frontend (React + Vite + TypeScript)

- `PredictForm.tsx`: the 12 inputs + model dropdown → `POST /predict` → show price.
- `HistoryList.tsx`: `GET /predictions` → table, refreshes after each submit.
- `api.ts`: typed client; types mirror `schemas.py` (keep them in sync by hand —
  simplest; note the option to codegen from OpenAPI as a Tier C nicety).

🧪 **Component unit test** (Vitest + Testing Library) — *learning: test behavior,
not implementation.*
- render `PredictForm`, fill fields, mock `fetch`, click submit → assert the
  displayed price appears.

🧪 **End-to-end test** (`tests/e2e/predict.spec.ts`, Playwright) — *learning: the
one test that exercises browser→API→DB for real.*
- against a running stack: fill the form → submit → assert price renders → assert
  the new row appears in the history list. Keep it to **one happy path**.

### A8 — Load baseline (`tests/load/locustfile.py`)

- One `HttpUser` task: `POST /predict` with a random-but-valid body, random model.
- Run `make load` at 10 / 100 / 1k users against `direct` mode; save the CSV
  Locust emits (`--csv`). This is the **baseline** the streaming study compares to.

✅ **Tier A exit criteria**
- [ ] `make seed && make train` populate DB + registry.
- [ ] `docker compose up` (base file) serves API + frontend; the e2e test passes.
- [ ] All unit + integration + contract tests green (`make test`).
- [ ] Locust baseline numbers recorded in `docs/load-baseline.md`.

---

# Tier B — Streaming + observability

**Goal:** flip `SERVING_MODE=streaming` and the *same* request now travels
FastAPI → Kafka → Spark → Postgres → back to the user, with Grafana showing it
move. Then prove the queue's value under load.

**Stack adds:** Kafka (KRaft, 1- then 3-broker) · Spark Structured Streaming ·
Prometheus · Grafana · kafka-exporter · node-exporter.

### B1 — Kafka 1-broker compose (`docker-compose.kafka-1broker.yml`)

- Single KRaft broker (no ZooKeeper). Create topics `prediction-requests` and
  `prediction-results` (a small init container running `kafka-topics.sh`, or
  `KAFKA_CREATE_TOPICS`). Start with **3 partitions** on requests to study
  consumer-group scaling.

✅ **Done:** `kafka-topics --describe` lists both topics with the expected
partition count.

### B2 — Streaming predictor (`serving/streaming.py`)

- `StreamingPredictor`: produce a JSON message to `prediction-requests` with a
  generated `request_id` (uuid) + features + model + a `trace_id`. Then **await
  the result**: simplest first = short-poll the `predictions` table for the row
  keyed by `request_id`; upgrade to SSE once poll works.
- The gateway returns the same `PredictResponse`. `latency_ms` now spans the whole
  round trip (this is the interesting number).

### B3 — Spark consumer (`spark/consumer.py`)

- `readStream` from `prediction-requests` → parse JSON → load the MLflow model
  (same `models:/…@production` URI as direct mode — *this is the point*) → predict
  → write to Postgres `predictions` (via `foreachBatch` + JDBC) **and** produce to
  `prediction-results`.
- Stateless map job on purpose (windowed/stateful version is a Future Improvement).

🧪 **Streaming integration test** (`tests/integration/test_streaming.py`) —
*learning: async result delivery is testable.* Use `testcontainers` Kafka +
Postgres (Spark can be a thin local consumer for the test, or run the real job):
- produce one request message → poll `predictions` until the row appears (timeout
  ~30s) → assert `predicted_price` present and `serving_mode == "streaming"`.

🧪 **Contract test (reused):** run the Tier A contract test with
`SERVING_MODE=streaming` → assert identical response shape. *This is the tier's
proof that the flag is transparent.*

### B4 — Observability (`docker-compose.observability.yml`)

- FastAPI: `prometheus-fastapi-instrumentator` exposes `/metrics` with latency
  histograms **labeled by `model` and `serving_mode`**.
- `kafka-exporter` → consumer lag, offsets. `node-exporter` → host. Spark → JMX/
  Prometheus servlet.
- Prometheus scrape config in `infra/prometheus/prometheus.yml`.
- Grafana **provisioned as code** (`infra/grafana/provisioning/`): datasource +
  the four dashboards from the plan. Dashboard #1 (Data-Flow) is the headline.

✅ **Done:** submit a prediction in `streaming` mode and watch the Data-Flow
dashboard show ingress RPS → offset growth → consumer lag → Spark processing rate
→ predictions/sec. Screenshot it for the README.

🧪 **Smoke test** (`tests/integration/test_metrics.py`) — *learning: metrics are
an API too.*
- after a few predictions, `GET /metrics` contains
  `http_request_duration_seconds` with a `serving_mode="streaming"` label.

### B5 — Kafka 3-broker overlay (`docker-compose.kafka-3broker.yml`)

- 3 KRaft brokers, replication factor 3, same topic names. Document ISR,
  under-replicated partitions, and rebalance behavior when a broker dies. The
  Kafka-health dashboard shines here.

### B6 — Load & scale study (the money graph)

- Re-run the Locust sweep in **`direct` vs `streaming`**. Capture: sync tail
  latency exploding vs the queued path holding while **consumer lag** rises.
- `docker compose --scale spark-consumer=N`; re-run at 1 vs N consumers; watch lag
  drain faster. Record latency-vs-concurrency and throughput-vs-concurrency in
  `docs/load-study.md` (plots from Grafana or D3).

✅ **Tier B exit criteria**
- [ ] Streaming path e2e works; contract test passes in both modes.
- [ ] Data-Flow dashboard demonstrably "breathes" under Locust load.
- [ ] 1- and 3-broker overlays both run; replication behavior documented.
- [ ] Load study table + plots committed.

---

# Tier C — Production depth

**Goal:** make it look like something you'd actually run — containerized,
CI-gated, drift-monitored, hardened at the edge, with explainability visuals.

### C1 — Containerization

- Multi-stage `Dockerfile` for backend (builder installs deps → slim runtime) and
  frontend (node build → nginx serve). `docker compose up` brings up the whole
  stack (base + overlays) with one command via a `COMPOSE_FILE` env or Make target.

✅ **Done:** a clean machine runs the full stack from `git clone` + `make up`.

### C2 — CI/CD (`.github/workflows/ci.yml`)

Jobs, in order, fail-fast:
1. **lint** — `ruff check` + `ruff format --check`; frontend `eslint` + `tsc`.
2. **unit + integration** — `pytest` (testcontainers works in GH Actions).
3. **model-regression gate** — 🧪 *learning: block a merge on model quality.*
   Load the champion's stored holdout metric; retrain candidate; **fail if
   `rmse` regresses beyond a tolerance** (e.g. >2%).
4. **build** — build backend + frontend images (push optional).

✅ **Done:** a PR that worsens the model or breaks a test goes red.

### C3 — Drift monitoring (Evidently)

- Job compares logged live predictions/features vs the training distribution →
  Evidently HTML report + a numeric drift score pushed to Prometheus (pushgateway
  or a `/drift-metrics` endpoint). Grafana alert fires when drift crosses a
  threshold. (Closed-loop retraining stays a Future Improvement.)

### C4 — D3 explainability views (`frontend/src/components/explain/`)

- **LinReg:** coefficient bars + regression line/plane + residual scatter.
- **LightGBM:** r2d3-style recursive feature-space partition from tree splits.
- Backend exposes the needed data: `GET /explain/linreg` (coefficients) and
  `GET /explain/lightgbm` (tree/split structure, e.g. `model.booster_.dump_model()`).

🧪 **Component test:** feed the D3 component fixed fixture data → assert the right
number of bars/nodes render (SVG element count). *Learning: even viz is testable.*

### C5 — Edge & resilience

- **Rate limiting / load-shedding** at ingress (`slowapi` or nginx `limit_req`).
- **Schema validation** already via Pydantic; add value-range checks (pandera on
  the training side).
- **Basic auth** (API key header) on `/predict`.
- 🧪 **Chaos drill** (`tests/chaos/kill_broker.sh`) — *learning: resilience is a
  test.* Under Locust load, `docker kill` a Kafka broker → assert (a) no requests
  are lost once recovered, (b) consumer lag spikes then drains, (c) Grafana shows
  the dip-and-recover. Repeat killing a Spark consumer.

🧪 **Auth + rate-limit integration tests:** request without API key → `401`;
exceed the limit → `429`.

✅ **Tier C exit criteria**
- [ ] Full stack containerized; CI green with the model-regression gate active.
- [ ] Drift report generates; Grafana alert wired.
- [ ] Both D3 explainability views render from live model data.
- [ ] Chaos drill documented with before/after Grafana screenshots.

> **Tier C.5 (Kubernetes + HPA)** is specced in `PROJECT_PLAN.md`; it's an
> infra-only layer over Tier C (move the *stateless* serving pods to k3d, add
> probes + HPA on Kafka-lag/CPU, re-run the Locust sweep and watch pods scale).
> No new app code, so no new app tests — the "test" is the autoscaling demo +
> a pod-delete chaos drill. Build it only after Tier C is solid.

---

# Tier D — Stretch

**Goal:** justify the heavy tools by giving them real volume and orchestration.
Pick à la carte; none are dependencies.

### D1 — Data amplification
- Sample-and-perturb the 545 rows → millions (add gaussian noise to numerics,
  resample categoricals within observed frequencies). Write to Postgres/Parquet.
- 🧪 **Property test** (`hypothesis`): amplified rows keep column invariants
  (`area > 0`, `furnishingstatus ∈ enum`, price non-negative). *Learning:
  property-based testing over example-based.*

### D2 — Airflow orchestration
- DAG: `seed → train → register` with dependencies + retries. Manual trigger is
  fine; scheduling optional.
- 🧪 **DAG-integrity test** (`pytest`): import all DAGs → assert no cycles, no
  import errors, expected task ids present. *Learning: pipelines are code you test
  before running.*

### D3 — Feast feature store
- Define feature views over housing features; Redis online store, Postgres/Parquet
  offline. Training reads offline; serving reads online (contrast latency).
- 🧪 **Integration test:** materialize → `get_online_features` returns the same
  values as the offline source for a known key.

### D4 — OpenTelemetry tracing → Tempo/Jaeger
- Instrument FastAPI + Spark consumer; **propagate `trace_id` through Kafka
  headers** so one prediction is a single span waterfall gateway→Kafka→Spark→store.
- ✅ **Done:** open one trace in Tempo/Jaeger and see all four spans linked. This
  is the ultimate data-flow visualization — the "test" is the screenshot.

### D5 — LightGBM GPU training (RTX 3090)
- Train with `device="gpu"` histogram; benchmark vs CPU on the amplified dataset.
- ✅ **Done:** a benchmark table (train time, rmse) CPU vs GPU in `docs/`.

✅ **Tier D exit criteria:** any subset done, each with its exit artifact
(test passing, benchmark table, or trace/screenshot). No requirement to do all.

---

## Cross-cutting conventions

- **One contract, two modes.** `PredictRequest`/`PredictResponse` never change
  between `direct` and `streaming`. The contract test enforces it.
- **Same model URI everywhere.** Direct path and Spark job both resolve
  `models:/<name>@production`. Never hand-copy weights.
- **Tests live next to what they prove** and run in CI from Tier C on. Aim for the
  pyramid: lots of fast unit tests, a solid ring of integration tests, a few e2e,
  one load scenario per mode.
- **Docs as deliverables.** `docs/load-baseline.md`, `docs/load-study.md`,
  chaos and GPU benchmark notes are graded artifacts, not afterthoughts.
- **Makefile is the interface.** Every routine action is one `make` target so the
  README stays short and CI reuses the same commands.

## Suggested build order (checklist)

1. A1→A2→A3→A4 (data + models ready, unit/integration tests green)
2. A5→A6 (API + contract test) → A7 (frontend + e2e) → A8 (load baseline)
3. B1→B2→B3 (streaming path + its integration test) → B4 (observability)
4. B5 (3-broker) → B6 (load study, the money graph)
5. C1→C2 (containers + CI gate) → C3→C4→C5 (drift, D3, edge, chaos)
6. C.5 if desired, then cherry-pick Tier D items.
