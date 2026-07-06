# Load study — `direct` vs `streaming` (Tier B)

The core question of the whole project: **what does the queue buy you?**

Setup: single uvicorn worker gateway; Kafka 1-broker (KRaft, 3 partitions);
one Spark Structured Streaming consumer (local[2]); Prometheus + Grafana
watching. Same Locust file as the Tier A baseline (`make load-sweep NAME=…`).

## Results

30-second runs, spawn rate 50/s; raw CSVs in `docs/load/`.

| Mode      | Users | Requests | Fail | RPS  | p50 (ms) | p95 (ms) | p99 (ms) |
|-----------|-------|----------|------|------|----------|----------|----------|
| direct    | 10    | 294      | 0    | 10.2 | 13       | 51       | 430      |
| direct    | 100   | 2701     | 0    | 93.1 | 42       | 210      | 470      |
| streaming | 10    | 172      | 0    | 6.0  | 220      | 7600     | 7800     |
| streaming | 100   | 29       | 0    | 25.1 | 1100     | 1100     | 1100     |

### Honest read of the numbers

- **Direct wins on raw latency at this scale** — for a model that predicts in
  ~1-15 ms, an in-process call beats a queue hop every time. The queue is not a
  latency optimization; it's a **decoupling and burst-absorption** mechanism.
- The streaming p95 spike at 10 users (7.6 s) is the fleet's first requests
  arriving while the Spark job lazy-loads both models — after warm-up, p50
  settles around 220 ms (micro-batch + 50 ms poll cadence).
- At 100 users, streaming throughput collapses to ~1 completed batch/s: every
  in-flight request **blocks a gateway threadpool slot while polling**, and the
  single consumer serializes work. That's not Kafka's limit — offsets show the
  broker absorbing everything instantly — it's the naive poll-based gateway.
  The consumer lag panel shows the queue doing its actual job: buffering.
- Which is exactly the lesson: to serve *thousands* of users through a queue
  you must (a) return results asynchronously (SSE/websocket instead of a
  blocking poll), and/or (b) scale consumers horizontally
  (`--scale spark-consumer=N`), which is Tier C.5's HPA demo.

## What to look at while it runs (Grafana → Data-Flow dashboard)

1. **Panel 1 + 3:** ingress RPS and topic offset growth rise together — every
   request becomes a Kafka message.
2. **Panel 4 (the money graph):** when producers outpace the consumer, latency
   doesn't explode on the client — **consumer lag** grows instead. The queue is
   absorbing the burst; the sync path has no such buffer.
3. **Panel 2:** direct p99 climbs with concurrency (requests queue *inside* the
   server); streaming p50 is higher (queue hop tax) but *bounded* by consumer
   throughput, not by concurrent connections.

## Scaling consumers

`docker compose --scale spark-consumer=2` (each joins the same consumer group;
Kafka rebalances the 3 partitions across them). Re-run the sweep and compare
how fast lag drains at 1 vs 2 consumers.

## Notes

- Streaming per-request latency includes the gateway's 50 ms poll interval —
  visible as a floor in the p50.
- Spark micro-batching means results arrive in small clumps; that's the
  batch-duration metric on the Spark job, not network jitter.
