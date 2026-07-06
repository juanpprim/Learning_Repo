# Real-Time ML Platform — Project Plan (v2)

> Capstone that ties the Learning Repo tracks together into one runnable app.
> **Domain:** house-price prediction. A batch-loaded housing dataset trains two
> models; **only the live user-prediction path is streamed** through Kafka +
> Spark Structured Streaming, with a flag to fall back to a simple direct path.
> Full open-source observability so the data flow is *visible* end-to-end.

Supersedes the v1 note in Obsidian (`Real-Time ML Platform - Project Plan`).

---

## Locked decisions (this revision)

| # | Decision | Rationale |
|---|----------|-----------|
| 1 | **Initial/reference data is batch-loaded, never streamed.** Housing CSV → Postgres once via a seed script. | The dataset is static; streaming a fixed 545-row file would be theatre. |
| 2 | **Streaming applies only to live user predictions.** `SERVING_MODE` flag: `streaming` (Kafka→Spark) or `direct` (in-process call). | Lets you A/B the queue's value and run a lightweight mode when infra isn't needed. |
| 3 | **Two models: LightGBM + Linear Regression.** Both tracked in MLflow, registered, served via FastAPI, selectable per request. | Contrast a tree model vs a linear model on accuracy *and* serving latency. |
| 4 | **Two Kafka topologies: 1-broker and 3-broker (KRaft).** Separate compose files. | 1-broker = simplest partition/consumer-group study; 3-broker = replication & rebalancing. |
| 5 | **Observability = Prometheus + Grafana + exporters (+ optional OTel tracing).** | Visualize the whole request→queue→spark→prediction flow live, all open source. |

---

## System specs (local cluster host)

| Component | Spec |
|-----------|------|
| CPU | Intel i7-6700K @ 4.0 GHz — 4 cores / 8 threads |
| RAM | 62 GB (≈51 GB free) |
| Storage | ≈380 GB free (LUKS-encrypted LVM) |
| GPU | NVIDIA RTX 3090 — 24 GB VRAM (LightGBM GPU histogram optional) |

Docker containers, shared kernel. In `direct` mode the stack is tiny (~4 GB);
full `streaming` mode with Spark + observability is ~18–20 GB, leaving ample headroom.

---

## Architecture

```
                      ┌──────────────────────────────────────────┐
  BATCH (no stream)   │  seed_data.py:  Housing.csv → Postgres    │
                      │  (reference data + training corpus)       │
                      └───────────────┬──────────────────────────┘
                                      │ read once
                      ┌───────────────▼──────────────────────────┐
   TRAINING           │  train.py → MLflow                        │
                      │   • model_a: LinearRegression (sklearn)   │
                      │   • model_b: LightGBM regressor           │
                      │  both logged + registered (Production)    │
                      └───────────────┬──────────────────────────┘
                                      │ load from MLflow Registry
                                      ▼
  LIVE PREDICTIONS (streamed)   FastAPI  (crud + gateway)
      user ──POST /predict──►  ├─ SERVING_MODE=direct ─────────► in-process model.predict()  ──┐
      {features, model}        │                                                               │
                               └─ SERVING_MODE=streaming ──► Kafka topic: prediction-requests   │
                                                                     │                          │
                                                       Spark Structured Streaming consumer      │
                                                       (loads MLflow model, predicts)           │
                                                                     │                          │
                                                            Kafka topic: prediction-results     │
                                                                     │                          │
                               ◄── SSE / poll ── result store (Postgres) ◄─── writer ───────────┘

  OBSERVABILITY (always on):  FastAPI /metrics ─┐
                              kafka-exporter ───┤
                              spark JMX/Prom ───┼─► Prometheus ─► Grafana dashboards
                              node-exporter ────┘        (+ optional OTel → Tempo/Jaeger traces)

  FRONTEND (React + D3):  prediction form · history · Grafana-style flow panel · r2d3 model view
```

---

## The `SERVING_MODE` flag

Single env var read by the FastAPI gateway:

- `SERVING_MODE=direct` — gateway calls the loaded MLflow model in-process. No
  Kafka, no Spark. Lowest latency; used for dev, unit tests, and as the
  **synchronous baseline** in the load study.
- `SERVING_MODE=streaming` — gateway produces the request to `prediction-requests`,
  a Spark Structured Streaming job consumes → predicts → emits to
  `prediction-results`; gateway returns via SSE (or short-poll on the result store).
  This is the path that demonstrates queue backpressure and horizontal scale.

Same request/response contract in both modes so the frontend and load tests don't change.

---

## Two models (both via MLflow + FastAPI)

| | Linear Regression | LightGBM |
|---|---|---|
| Library | scikit-learn | lightgbm (CPU; optional GPU histogram on the 3090) |
| Strength | tiny, fast, interpretable coefficients | non-linear, higher accuracy, heavier |
| Serving latency | ~sub-ms | higher — good contrast under load |
| D3 explainability view | regression line/plane + residuals + coefficient bars | **r2d3-style** recursive feature-space partition from the tree splits |

`/predict` takes a `model` field (`linreg` \| `lightgbm`). Both are registered in
the MLflow Model Registry and loaded by alias, so the Spark job and the direct
path resolve them identically. Comparing their p50/p99 under load is itself a
deliverable.

> Note: LightGBM is tree-based, so it still gives you the animated
> decision-boundary aesthetic from r2d3 even though the target (price) is a
> regression. No need to fabricate a classification label.

---

## Two Kafka topologies

Two compose overlays, one app:

- `docker-compose.kafka-1broker.yml` — 1 broker (KRaft), N partitions. Study
  consumer-group scaling and partition→consumer assignment.
- `docker-compose.kafka-3broker.yml` — 3 brokers (KRaft), replication factor 3.
  Study replication, ISR, under-replicated partitions, and rebalancing when a
  broker is killed.

Topic layout is identical (`prediction-requests`, `prediction-results`); only
broker count and replication factor change. Document throughput/lag differences
between the two under the same load.

---

## Observability & telemetry (visualize the data flow)

All open source. Goal: watch a request travel request → queue → Spark → result **live**.

**Metrics — Prometheus scrapes:**
- **FastAPI** via `prometheus-fastapi-instrumentator`: request rate, latency
  histogram (p50/p95/p99), in-flight, errors, **labeled by `model` and `serving_mode`**.
- **Kafka** via `kafka-exporter`: per-partition **consumer lag**, offsets,
  message rate, under-replicated partitions.
- **Spark Structured Streaming** via the Prometheus servlet / JMX exporter:
  input rate, processing rate, batch duration, scheduling delay.
- **Host** via `node-exporter`: CPU, RAM, disk.

**Grafana dashboards (provisioned as code):**
1. **Data-Flow / Pipeline** *(the headline)* — ingress RPS → topic offset growth
   → consumer lag → Spark processing rate → predictions/sec out. One screen that
   shows the system "breathing" under load.
2. **Serving latency & throughput** — p50/p95/p99 and RPS split by model and mode.
3. **Kafka health** — lag per partition, broker/ISR status (shines in 3-broker mode).
4. **Host resources** — during load tests.

**Tracing (optional stretch, best "flow" visualization):** OpenTelemetry SDK in
FastAPI + the Spark consumer → **Tempo or Jaeger**. Propagate a trace-id through
the Kafka message headers so a single prediction shows a span waterfall across
gateway → Kafka → Spark → result store. This literally renders the data-flow path.

**Logs (optional):** Loki + Promtail for structured JSON prediction logs,
correlated with metrics/traces in one Grafana.

---

## Load & scale study (why the queue exists)

Dedicated, reproducible benchmark — the core of the "few → hundreds → thousands
of simultaneous users" goal.

- **Locust** with a configurable concurrency knob; sweep 10 / 100 / 1k / 5k users.
- Compare **`direct` (synchronous)** vs **`streaming` (queued)**: watch the sync
  path's tail latency explode while the queued path holds and **Kafka consumer
  lag** rises instead — the money graph.
- Scale consumers/gateway: `docker compose --scale` behind nginx/traefik; re-run
  the sweep at 1 vs N replicas.
- Emit a results table + plots of **latency vs concurrency** and **throughput vs
  concurrency** (render with the same D3 you're learning, and/or read straight
  from Grafana).

---

## Build phases (tiered so there's a finishable MVP)

### Tier A — Core walking skeleton (satisfies the whole brief end-to-end)
- [ ] `seed_data.py`: Housing.csv → Postgres (batch, idempotent).
- [ ] `train.py`: LinearRegression + LightGBM → MLflow, both registered.
- [ ] FastAPI gateway: `/predict` (model + `SERVING_MODE`), `/health`, `/metrics`.
- [ ] `direct` mode working end-to-end first.
- [ ] React frontend: prediction form + history list.
- [ ] Locust load sweep against `direct` mode; record baseline latency/throughput.

### Tier B — Streaming + observability (the heart of the project)
- [ ] Kafka **1-broker** compose (KRaft); topics `prediction-requests` / `-results`.
- [ ] Spark Structured Streaming consumer: load MLflow model → predict → emit results.
- [ ] Gateway `streaming` path with SSE/poll return; flag flips cleanly.
- [ ] Prometheus + Grafana + kafka-exporter + node-exporter, dashboards provisioned.
- [ ] Data-Flow dashboard shows a live request traversing the system.
- [ ] Kafka **3-broker** compose overlay; document replication/rebalance behavior.
- [ ] Load study: `direct` vs `streaming`, 1 vs N consumers, lag captured.

### Tier C — Production depth
- [ ] Multi-stage Dockerfiles; full `docker compose up` for the whole stack.
- [ ] CI/CD (GitHub Actions): ruff + pytest + model-regression gate + image build.
- [ ] Evidently drift report over logged predictions; alert wired into Grafana.
- [ ] D3 model-explainability views: r2d3 partition (LightGBM) + regression/residuals (LinReg).
- [ ] **Edge & resilience:** rate limiting (load-shedding at the ingress),
      request-schema validation (pandera/Pydantic), basic auth on the gateway;
      **chaos drills** — kill a Kafka broker / container mid-load and watch
      recovery in Grafana (consumer lag spike → drain).

### Tier C.5 — Kubernetes + HPA autoscaling
> Layer this on *after* Tier B works in docker-compose. Only the stateless
> serving layer moves to k8s; the heavy stateful infra stays in compose (or Helm).
- [ ] Local cluster with **k3d** (or kind); load/push the serving images.
- [ ] Move the **stateless serving layer** (FastAPI gateway + prediction
      consumers) to Deployments + Service/Ingress. Keep Kafka, Spark, MLflow,
      Postgres, Prometheus, Grafana in docker-compose.
- [ ] Liveness/readiness probes + resource requests/limits per pod.
- [ ] **HorizontalPodAutoscaler** on gateway/consumers (CPU, or a custom
      latency / Kafka-consumer-lag metric via prometheus-adapter).
- [ ] kube-state-metrics → Prometheus; Grafana panel showing **pod count scaling
      up as RPS / consumer lag rises**.
- [ ] Re-run the Locust sweep and watch pods autoscale under load — the concrete
      "few → thousands of users" demo.
- [ ] Chaos drill: delete a pod mid-load; confirm the Service reroutes and the
      HPA recovers. (Mind the 4-core host — don't also run Spark 3-broker + full
      stack simultaneously.)

### Tier D — Stretch (use amplified synthetic data so the big tools earn their place)
- [ ] Amplify housing rows → millions via sampling/perturbation for volume.
- [ ] Airflow DAG orchestrating seed → train → register.
- [ ] Feast online/offline feature store (Redis online).
- [ ] OpenTelemetry tracing → Tempo/Jaeger across gateway → Kafka → Spark.
- [ ] LightGBM GPU histogram training on the RTX 3090; benchmark vs CPU.

---

## Track → phase mapping

| Track | Subtopic | Tier |
|-------|----------|------|
| App Development | Backend API (FastAPI) | A |
| MLOps | Experiment Tracking (MLflow) | A |
| App Development | React Frontend | A |
| Parallel/Distributed | Python Concurrency (async gateway) | A |
| Data Engineering | Kafka (1- & 3-broker) | B |
| Data Engineering | Spark (Structured Streaming) | B |
| MLOps | Model Serving | B |
| MLOps | Monitoring & Observability | B |
| MLOps | CI/CD for ML | C |
| App Development | Full-Stack Capstone (D3 views) | C |
| Data Engineering | Airflow / dbt / Warehouses | D |
| MLOps | Feature Stores (Feast) | D |
| Parallel/Distributed | Dask/Ray · Distributed Training · GPU/CUDA | D |

---

## Data source

Kaggle — Housing Prices (`yasserh/housing-prices-dataset`): 545 rows, target
`price`; features `area, bedrooms, bathrooms, stories, mainroad, guestroom,
basement, hotwaterheating, airconditioning, parking, prefarea, furnishingstatus`.
Small on purpose for the model itself; Tier D amplifies it for the scale tools.

---

## Future improvements

Deferred ideas — champion/challenger routing, closed-loop retraining, stateful
stream analytics, cloud deployment, and explicitly-skipped options — are captured
in [`FUTURE_IMPROVEMENTS.md`](FUTURE_IMPROVEMENTS.md) as a reference backlog.

---

## Status
- [x] Plan revised (v2)
- [ ] Tier A — Core walking skeleton
- [ ] Tier B — Streaming + observability
- [ ] Tier C — Production depth
- [ ] Tier C.5 — Kubernetes + HPA autoscaling
- [ ] Tier D — Stretch
