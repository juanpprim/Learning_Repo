# Learnings — building the Real-Time ML Platform (Tiers A → D)

What actually got learned, including the failures. Companion to the per-topic
notes (`load-baseline.md`, `load-study.md`, `kafka-3broker-notes.md`,
`k8s-hpa-notes.md`, `tier-d-notes.md`).

---

## Architecture lessons

**A frozen contract is what makes a flag cheap.** `PredictRequest`/
`PredictResponse` never changed between `direct` and `streaming`, so the
frontend, Locust files, and e2e tests worked unmodified when the entire
serving path was swapped. The contract test (parametrized over both modes) is
tiny but it's the load-bearing wall.

**One seam, not many.** All mode-specific behavior lives behind the
`Predictor` protocol (`predict(req, session) -> PredictResponse`, each mode
owning its persistence). The first design had the route persisting — that
broke as soon as streaming arrived, because in that mode *the consumer*
writes the row. Lesson: put the seam where responsibilities genuinely
diverge, not where it first looks convenient.

**Same model URI everywhere.** Both the in-process path and the Spark
consumer load `models:/<name>@production`. When training re-registers, both
paths pick it up identically — no weight copying, no version skew. The MLflow
alias is doing real architectural work.

**The queue is not a latency optimization.** Direct mode beats streaming on
latency at every load level we measured (13 ms vs 220 ms p50). What the queue
buys is *decoupling*: the broker absorbed every burst instantly while
consumer backlog grew — visible as the offset-delta panel. Say this upfront
in any design discussion; "Kafka will make it faster" is the wrong story.

## Streaming lessons

**Kafka advertised listeners = one per client audience.** Three kinds of
clients (compose containers, host processes, k3d pods) needed three
listeners, because Kafka *hands back* the advertised address after bootstrap
and it must be resolvable from the client. Nearly every "can't connect to
Kafka" incident in this project was really an advertised-listener problem.

**Spark's Kafka source commits no consumer group.** Offsets live in Spark
checkpoints, so `kafka_consumergroup_lag` is empty for it and kafka-exporter
can't see backlog. The fix that taught the most: derive backlog as
requests-topic offsets minus results-topic offsets — a proxy you fully
understand beats a metric that silently reads zero.

**Blocking poll-for-result is the scaling ceiling.** The gateway holds a
threadpool slot for the entire queue round trip. At 100 users that collapsed
throughput (29 completions/30 s in compose; readiness-flap 404s in k8s). The
architecture was never wrong — the *return path* was. Async/SSE result
delivery is the single highest-leverage improvement (see
FUTURE_IMPROVEMENTS).

**Replication ≠ backup, it's availability.** rf=3/minISR=2: killing a broker
shrank ISR and failed over leaders in seconds with zero write loss; the
restarted broker caught up and did *not* take leadership back (no failback —
Kafka avoids churn).

## Observability lessons

**Label by the dimensions you'll compare.** `predictions_total` and
`prediction_latency_seconds` labeled by `model` and `serving_mode` made every
study a one-line PromQL query. Generic HTTP metrics alone would have answered
none of the interesting questions.

**Metrics are an API — test them.** The metrics smoke test asserts exact
series names and labels; a rename would blank the dashboards silently
otherwise. Dashboards-as-code (provisioned JSON/YAML) made every panel
reviewable in a diff.

**Watch the system breathe before trusting it.** The Data-Flow dashboard
(ingress RPS → offsets → backlog → predictions/s) caught issues faster than
logs did — e.g., the consumer silently doing nothing after the topic-creation
race was a flat processing-rate panel.

## Kubernetes lessons (Tier C.5)

**HPA is proportional control and it shows.** CPU 115% of request → scale to
2 → CPU 57%, right at the 60% target. Setting a *low* CPU request (200m) is
what made the demo work on a 4-core host — utilization is measured against
the request, not the node.

**Probes share the starved process.** Under CPU throttling the same worker
pool served `/health`, so saturated pods flapped NotReady and Traefik
returned 404s for 76% of requests. Autoscaling didn't fail — the pods lied
about readiness. Fixes ranked: shed load at the ingress (the Tier C rate
limiter), make the hot path non-blocking, give probes headroom.

**Autoscaling ≠ load-shedding.** Max replicas is a budget, not a promise.
Something must still say "no" past capacity, and it should be the cheapest
component (429 at the edge), not the most expensive one (a timed-out queue
round trip).

**`host.k3d.internal` is the pragmatic bridge.** Hybrid k8s-pods →
compose-services networking is fine for learning setups, as long as anything
that *advertises its own address* (Kafka) gets a listener for that name.

## Testing lessons

**Each layer caught different bugs.** Schema tests caught contract typos;
testcontainers integration tests caught the SQLAlchemy-session snapshot issue
(`rollback()` needed in the poll loop) and proved seed idempotency; the
streaming test with a real broker caught serialization details mocks would
have hidden; property tests (hypothesis) forced the amplifier to handle
`rows=1`; the e2e test caught a CORS config that every lower layer passed.

**Test the boundary you own, fake the one you don't.** FakePredictor for API
tests, fake model for predictor tests, real Postgres/Kafka for wiring tests.
The stub Spark consumer (same message contract, no Spark) kept the streaming
round trip testable in seconds.

**Gate models like code.** The regression gate (candidate RMSE vs frozen
baseline, ±2%) turns "did my refactor hurt the model?" into a CI failure
instead of a production surprise. Deterministic synthetic data is what makes
the gate reproducible.

## Compatibility war stories (each cost real time)

| Symptom | Root cause | Fix |
|---|---|---|
| MLflow 404 on `log_model` | 3.x client vs 2.x server REST mismatch | pin server image to client version |
| MLflow 403 "DNS rebinding" from containers | MLflow 3 rejects non-localhost Host headers | `--allowed-hosts` |
| `apt install openjdk-17` failing in Docker | `python:3.12-slim` silently moved to Debian trixie | pin `-bookworm` |
| Spark job dead on arrival | subscribed before topics existed | `depends_on: kafka-init: service_completed_successfully` |
| Airflow task: `'Connection' has no attribute 'cursor'` | pandas `to_sql` needs SQLAlchemy 2.x; Airflow pins 1.4 | plain SQL inserts in the seed script |
| LightGBM import crash in Airflow | stock image lacks `libgomp1` | tiny `dockerfile_inline` layer |
| DAG trigger stuck "queued" forever | fresh metadata DB → DAG paused by default | unpause before trigger (baked into `make airflow-run`) |
| `docker compose` "unknown command" | dangling Docker-Desktop symlinks in `~/.docker/cli-plugins` | replace with real binaries |
| Airflow DAGs invisible to git | repo-root `.gitignore` ignores every `dags/` dir | folder named `airflow_dags/` |
| Shell dying with exit 144 | `pkill -f` matching its own command line | `pkill -f 'uvicorn[ ]app.main'` |

Meta-lesson: **version skew between cooperating environments** (backend venv,
Spark image, Airflow image, MLflow server) is the dominant failure category
in a multi-runtime system. Pin identically, and verify by *running the real
thing*, not by reading changelogs.

## Data lessons

**A deterministic synthetic fallback pays for itself.** Everything —
training, tests, CI, the regression gate — runs without Kaggle credentials,
and fixed seeds make metric assertions reproducible to the digit.

**Drift detection fired for a true reason on day one.** Locust generates
uniformly-random features; training data isn't uniform. Evidently flagged
58% of columns drifted — correct! Load-test traffic *is* distribution shift.
Good reminder that a drift alert needs a "what traffic is this?" question
attached before anyone retrains.
