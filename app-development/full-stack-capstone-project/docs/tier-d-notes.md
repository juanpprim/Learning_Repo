# Tier D notes — stretch items

Tier D is à la carte by design (spec: "any subset done, each with its exit
artifact"). Two items are implemented; the rest stay documented options.

## D1 — Data amplification ✅

`make amplify` (= `python -m ml.amplify --rows 1000000`): sample-and-perturb
the 545 rows into 1M — multiplicative gaussian jitter on `area`/`price`,
±1 steps on the small integer columns, categoricals drawn as-is.

Observed: **545 → 1,000,000 rows in 1.2 s, 10.0 MB parquet**
(`data/housing_amplified.parquet`). Columnar compression is the quiet lesson:
a million rows of this schema is *small*.

Exit artifact: `tests/unit/test_amplify.py` — **hypothesis property tests**
(schema invariants hold for any rows/seed), determinism-per-seed, and
actually-perturbs checks.

## D2 — Airflow orchestration ✅

`make airflow-up`: Airflow 3 standalone container, DAGs folder mounted from
`backend/airflow_dags/` (named that way because the repo root `.gitignore`
ignores every `dags/` directory).

`housing_pipeline` DAG: **seed → train → regression_gate** — the exact
commands the Makefile runs by hand, now with retries and dependency order.
Tasks run our unchanged `ml/` modules against the compose Postgres + MLflow.

Exit artifacts:
- `make airflow-check` — the DAG-integrity test (`dags list-import-errors`
  must be empty; the pipeline must appear in `dags list`).
- `make airflow-run` — trigger it end to end; watch at http://localhost:8080.

## Documented options (not implemented)

| Item | What it would add | Why deferred |
|------|-------------------|--------------|
| D3 Feast | online (Redis) vs offline feature reads | new infra + heavy dep for one lookup pattern |
| D4 OpenTelemetry → Tempo | span waterfall gateway→Kafka→Spark | best done after SSE replaces the poll return |
| D5 LightGBM GPU (RTX 3090) | CPU-vs-GPU training benchmark on the 1M-row set | pip lightgbm ships without CUDA; needs a custom build |

Each has a sketch in [`PROJECT_PLAN.md`](../PROJECT_PLAN.md) Tier D and
[`FUTURE_IMPROVEMENTS.md`](../FUTURE_IMPROVEMENTS.md).
