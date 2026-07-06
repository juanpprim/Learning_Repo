# Tier C.5 — Kubernetes + HPA notes (k3d)

Setup: k3d cluster (`make k3d-up`), gateway Deployment in `streaming` mode
reaching the compose stack via `host.k3d.internal` (Kafka got a third
listener that advertises that name — see `docker-compose.kafka-1broker.yml`).
HPA: CPU target 60% of a 200m request, min 1 / max 5. Manifests in `infra/k8s/`.

## Demo 1 — the money graph (30 users, `make k3d-watch-hpa` view)

| time | avg pod CPU (of request) | replicas |
|------|--------------------------|----------|
| 18:34:04 | 1% | 1 |
| 18:34:20 | 52% | 1 |
| 18:34:36 | **108%** | 1 |
| 18:34:52 | 115% | **2** |
| 18:35:24 | 68% | 2 |
| 18:35:40 | **57%** | 2 |

Load pushes one pod past the 60% target → HPA adds a pod → average CPU
falls back to ~57%, right at target. Proportional control working exactly as
designed. 2,177 requests at ~18 RPS, p50 630 ms (streaming round trip);
5% failures during the brief window while pod #2 warmed up.
Grafana: Data-Flow panel 9 shows the same story (pods vs RPS).

## Demo 2 — overload is a different lesson (100 users)

At 100 users the HPA maxed out at 5 replicas but **76% of requests failed
with Traefik 404s**. Why: each pod is CPU-limited to 500m and the streaming
path *blocks* a worker while polling for its result, so saturated pods
starved their own `/health` probes → readiness flapped → Traefik removed
pods from the endpoint set → instant 404s. One pod's liveness probe even
restarted it.

The lesson stack, in order:
1. Autoscaling is not load-shedding — the Tier C rate limiter should cap
   intake *before* pods choke (it was disabled for this run).
2. Blocking poll-for-result handlers scale terribly; the SSE/async return
   noted in the spec is the real fix.
3. Health probes share the same starved event loop — separate them from
   work, or give them headroom, or they lie under pressure.

## Demo 3 — pod-delete chaos drill (`make k3d-chaos`)

Deleted a gateway pod mid-traffic: **20/20 health checks succeeded** during
replacement; Deployment self-healed in ~15 s. Readiness gating means the
Service never routed to the not-yet-ready replacement.

## Operational notes

- 4-core host: run k3d alongside the **1-broker** compose overlay only.
- `host.docker.internal:8000` (Prometheus's gateway target) now reaches the
  k8s pods through the k3d loadbalancer — dashboards needed no changes.
- Deferred (documented, not built): prometheus-adapter for a
  Kafka-lag-based HPA metric; moving Spark consumers into k8s; managed-cloud
  deployment (see FUTURE_IMPROVEMENTS.md).
