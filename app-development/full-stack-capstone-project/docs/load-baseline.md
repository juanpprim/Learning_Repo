# Load baseline — Tier A, `direct` mode

Single uvicorn worker, models loaded in-process, Postgres in Docker.
Command: `uv run locust -f tests/load/locustfile.py --headless -u <N> -r 50 -t 30s`
(random model per request: ~50% linreg, ~50% lightgbm). Raw CSVs in `docs/load/`.

| Users | Requests | Fail | RPS  | p50 (ms) | p95 (ms) | p99 (ms) | max (ms) |
|-------|----------|------|------|----------|----------|----------|----------|
| 10    | 294      | 0    | 10.2 | 13       | 51       | 430      | 460      |
| 100   | 2701     | 0    | 93.1 | 42       | 210      | 470      | 780      |

## Reading the numbers

- At 10 users the sync path is comfortable: p50 ≈ 13 ms.
- At 100 users p50 already trebles (42 ms) and p95 quadruples (210 ms) —
  classic queueing-at-the-server behavior with one worker: requests wait in
  line for CPU, tail latency grows first.
- The p99 outliers (~430-470 ms) in both runs are the first requests hitting
  each model's lazy load + connection setup.

This table is the **baseline** the Tier B study compares against: the claim to
verify is that `streaming` mode holds latency flat under higher concurrency by
letting **Kafka consumer lag** absorb the burst instead of the request path.

*(Numbers above were captured on the i7-6700K host with synthetic data; rerun
`make load` after changing hardware or models.)*
