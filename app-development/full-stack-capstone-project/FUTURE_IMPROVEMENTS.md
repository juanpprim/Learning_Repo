# Future Improvements — Reference Backlog

Ideas considered for the Real-Time ML Platform but **deliberately deferred** to
keep the core plan finishable. Not scheduled; pull one in when the base tiers are
solid and you want a specific new skill. See [`PROJECT_PLAN.md`](PROJECT_PLAN.md)
for the committed scope.

---

## High ROI — reuse infrastructure already in the plan

### 1. Champion / challenger model routing (A/B + shadow)
You already train two models (LightGBM + Linear Regression); today they're only
user-selectable. Productionize the comparison:
- Designate LightGBM **champion**, Linear Regression **challenger**.
- **A/B:** route a configurable % of live traffic to the challenger.
- **Shadow:** send every request to both, serve only the champion, log both
  predictions for offline comparison (no user impact).
- Compare accuracy + latency on real traffic; promote via the MLflow registry.

**Learning:** progressive delivery, traffic splitting, online evaluation.
**Reuses:** both registered models, FastAPI gateway, Prometheus (label by variant).

### 2. Closed-loop retraining trigger
Turn the drift report from a dead-end into an automated loop:
- Evidently detects drift → fires an Airflow DAG (or webhook).
- DAG reruns `train.py` → registers a new model version.
- **Auto-promote only if it beats the champion** on a frozen holdout; otherwise
  keep the incumbent and alert.

**Learning:** continuous training (CT), model governance, promotion gates.
**Reuses:** Airflow (Tier D), MLflow registry, Evidently (Tier C).

### 3. Stateful stream analytics job
Add a *second* Spark Structured Streaming job alongside the prediction consumer:
- Windowed aggregation with watermarks: requests/min, rolling predicted-price
  distribution, late-data handling.
- Output feeds the Grafana Data-Flow dashboard.

**Learning:** the genuinely hard part of streaming — windowing, watermarks,
stateful ops, late/out-of-order events (the current Spark job is stateless map-only).
**Reuses:** Kafka topics, Spark, Grafana.

---

## Optional epilogue — the "true production" finale

### 4. Managed-cloud Kubernetes deployment
After the local k3d/kind tier (C.5), deploy the serving layer to a managed
cluster — **GKE Autopilot** or **EKS**. Adds a cloud load balancer, real ingress,
node autoscaling, and cloud-native observability.

**Caveat:** costs money; treat as a clearly-optional capstone, not a dependency.
**Learning:** cloud k8s, IAM, managed autoscaling, cost awareness.

---

## Explicitly skipped (diminishing returns for local learning)

| Idea | Why skipped |
|------|-------------|
| Terraform / IaC | Little value for a single local host; revisit only with the cloud epilogue. |
| Service mesh (Istio/Linkerd) | Heavy; the app has too few services to justify the complexity. |
| gRPC vs REST comparison | Interesting for latency, but niche vs the rest of the roadmap. |
| Multi-cloud | No learning payoff over single managed cluster; pure ops overhead. |

---

## Also worth a note if the mood strikes
- **Prediction caching (Redis):** cache repeated feature vectors → show latency
  drop under repeated queries. Pairs with the load study.
- **Data-quality contract (pandera/Great Expectations):** formal schema + value
  checks on incoming requests and training data (partly covered by Tier C edge
  validation — this is the deeper version).
- **Architecture Decision Records (ADRs):** short `docs/adr/` notes capturing why
  each major choice was made — good habit for a learning repo.

---

## Code-review backlog (review of the implemented Tiers A–D, 2026-07-06)

Concrete improvements found by reviewing the finished code. Ordered by
leverage; the first two were *observed* failing under load, not hypothesized.

### High — correctness / scalability under load

1. **Async result return for streaming mode** (`backend/app/serving/streaming.py`,
   `app/main.py`). The gateway blocks a threadpool slot for the whole queue
   round trip (sync `def` route + 50 ms Postgres polling). This is the proven
   ceiling: 29 completions/30 s at 100 users in compose; readiness-flap 404s
   in k8s. Fix: `async` route + SSE/WebSocket push, sourcing results from the
   `prediction-results` topic (or Postgres LISTEN/NOTIFY) instead of polling.
   This unlocks every scale number in the load studies.
2. **Load-shed before pods choke** — the slowapi limiter is **in-memory per
   process**, so with N gateway pods the effective limit is N× and each pod
   still self-saturates (the Tier C.5 overload run). Back it with Redis (one
   more compose service) or enforce at Traefik/nginx instead.
3. **Kafka producer `flush(5)` per request** (`streaming.py:48`) defeats
   batching and adds latency under concurrency. Use delivery callbacks and
   let librdkafka batch; surface produce errors via the callback.
4. **Malformed messages become garbage rows** (`spark/consumer.py`):
   unparseable JSON yields all-NULL structs that are inserted with
   `request_id = NULL`. Filter `request_id IS NOT NULL` after `from_json`
   and count rejects to a metric (poor-man's dead-letter queue).

### Medium — robustness / hygiene

5. **Double commit per direct prediction** (`serving/direct.py:46,50`): insert
   then latency-update = two round trips. Compute latency before a single
   insert (persistence cost can be its own metric if wanted).
6. **API-key comparison isn't constant-time** (`main.py:64`): use
   `secrets.compare_digest`. Same file: CORS is `allow_origins=["*"]` — fine
   for dev, but the app compose overlay should pin the frontend origin.
7. **`GET /drift` is unauthenticated, synchronous Evidently** — seconds of CPU
   per call = a free DoS lever. Require the API key and/or move it behind the
   Airflow DAG (D2 already orchestrates; add a `drift` task).
8. **Spark consumer opens a psycopg2 connection per micro-batch** and
   `collect()`s to the driver — fine at learning scale, documented as such,
   but a connection pool + `foreachPartition` is the natural next step.
9. **`predictions` table grows forever** — add a retention job (`DELETE WHERE
   created_at < now() - interval '30 days'`), which also keeps `/drift` and
   `/predictions` queries bounded.
10. **Global singletons for test reset** (`main._predictor`, `db._engine`,
    fixtures poking them back to `None`) — replace with a FastAPI app factory
    receiving `Settings`, so tests build isolated apps instead of mutating
    module state.

### Low — maintainability

11. **Frontend types are hand-mirrored from `schemas.py`** (`frontend/src/api.ts`
    says so). Generate from the OpenAPI schema (`openapi-typescript`) in a CI
    step so drift becomes a build failure.
12. **Dependency pins are triplicated by hand** (backend `uv.lock`, the Spark
    image `pip install`, the Airflow `_PIP_ADDITIONAL_REQUIREMENTS`) — the
    known skew hazard (see docs/LEARNINGS.md). Export one
    `uv export --format requirements` artifact and reuse it in both images.
13. **`ALTER TABLE IF NOT EXISTS` mini-migration** in the lifespan will not
    scale past a second column — adopt Alembic once the schema changes again.
14. **Playwright e2e isn't in CI** (needs a live stack). Add a compose-based
    job (`make up` + seed + train + e2e) as a nightly rather than per-PR.
15. **Grafana drift alert has no notification channel** — it fires in the UI
    only. Wire a contact point (even a webhook to a log) so "alert wired"
    means delivered, not just evaluated.
