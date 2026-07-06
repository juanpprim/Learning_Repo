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
