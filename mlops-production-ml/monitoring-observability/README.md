# Monitoring & Observability for ML

## Objectives
- Detect data drift and concept drift in production inputs/predictions.
- Instrument a serving app with structured logging and basic metrics.
- Understand the difference between traditional software observability
  (latency, error rate, throughput) and ML-specific monitoring (drift, staleness,
  fairness/quality degradation).

## Key concepts
- Data drift vs. concept drift vs. label drift.
- Statistical drift tests: population stability index (PSI), KL divergence,
  Kolmogorov-Smirnov test.
- Structured logging (JSON logs) and metrics (Prometheus-style counters/histograms).
- Alerting thresholds and on-call fatigue tradeoffs.

## Resources
- Evidently AI docs (drift detection library): https://docs.evidentlyai.com/
- "Designing Machine Learning Systems" (Chip Huyen) — monitoring chapter.
- Prometheus docs (metrics concepts): https://prometheus.io/docs/introduction/overview/

## Checklist
- [ ] Simulate drift: take a training dataset, generate a "shifted" version
      (e.g. resample a feature's distribution), and compute PSI/KS between them.
- [ ] Use Evidently (or a hand-rolled check) to generate a drift report.
- [ ] Add structured logging to a serving endpoint (reuse
      `model-serving-fastapi-docker/`) that logs each prediction + input features.
- [ ] Define and compute one custom "model health" metric over a batch of
      logged predictions.

## Mini-project
Simulate a production feed with gradually shifting input distributions, run
drift detection on rolling windows, and plot when your detector would have
fired an alert vs. when the model's actual accuracy started degrading.
