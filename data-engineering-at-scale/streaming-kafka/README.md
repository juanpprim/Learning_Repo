# Streaming with Kafka

## Objectives
- Understand pub/sub semantics: topics, partitions, producers, consumers, consumer groups.
- Produce and consume events from a local Kafka broker.
- Implement basic windowed aggregation over a stream.
- Reason about delivery guarantees (at-most-once / at-least-once / exactly-once)
  and why they matter for data pipelines.

## Key concepts

> **Deep dive:** open [`key_concepts.html`](key_concepts.html) in a browser for animated explanations of each concept below.
- Topics and partitions as the unit of parallelism and ordering.
- Offsets and consumer groups (how multiple consumers share a topic).
- Producer acks (`acks=0/1/all`) and idempotent producers.
- Windowing: tumbling vs. sliding windows for stream aggregation.
- Kafka vs. batch: why you'd choose streaming over periodic batch jobs.

## Resources
- Kafka docs — Introduction: https://kafka.apache.org/documentation/#gettingStarted
- Confluent Kafka Python client docs: https://docs.confluent.io/kafka-clients/python/current/overview.html
- "Kafka: The Definitive Guide" (free from Confluent).

## Checklist
- [ ] Run a local Kafka broker (`docker run` with a Kafka image, or Redpanda as
      a lighter-weight alternative).
- [ ] Write a producer that publishes JSON events to a topic.
- [ ] Write a consumer that reads from that topic and prints/aggregates events.
- [ ] Run two consumers in the same consumer group and observe partition rebalancing.
- [ ] Implement a simple tumbling-window count (e.g. events per 10-second window).

## Mini-project
Simulate a stream of user click events (a producer script generating random
events), consume them with a windowed aggregator that prints rolling counts
per event type, and document the delivery-guarantee tradeoffs you chose.
