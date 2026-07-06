# Kafka 3-broker replication notes (Tier B)

Topology: 3 KRaft brokers (`make up-streaming-3`), topics at
`--replication-factor 3 --config min.insync.replicas=2`, 3 partitions each.

## Observed drill: kill broker 2 mid-flight

`docker stop infra-kafka2-1`, then `kafka-topics.sh --describe`:

| Moment | Partition 0 ISR | Partition 1 leader | Availability |
|--------|-----------------|--------------------|--------------|
| healthy | `3,1,2` | (2 in replica set `1,2,3`) | writes OK |
| broker 2 down | `3,1` | **failed over to 1** | writes still OK |
| broker 2 back (+12 s) | `3,1,2` | still 1 (no failback) | writes OK |

What that demonstrates:

1. **ISR shrink, not outage.** With rf=3 and min.insync.replicas=2, losing one
   broker removes it from every partition's in-sync replica set but keeps the
   topic writable — producers with `acks=all` still get 2 acknowledgments.
2. **Leader election is automatic and fast.** Partitions led by broker 2 were
   re-led by a surviving replica within seconds; clients just retried.
3. **Rejoining is catch-up, not reset.** The restarted broker re-entered ISR
   once it replayed the log (~12 s here for a tiny log). Leadership does NOT
   automatically move back — Kafka avoids churn (until a preferred-leader
   election runs).
4. If a **second** broker died, writes would start failing
   (`NOT_ENOUGH_REPLICAS`) — min ISR 2 is the durability floor we chose.

Same drill visualized: Grafana → **Kafka Health** → "In-sync replicas per
partition" + "Under-replicated partitions" (spikes above 0 while the broker is
down, drains after it returns).

Contrast with the 1-broker topology: there, stopping the broker is a full
outage and the gateway's streaming path 504s — replication is availability.
