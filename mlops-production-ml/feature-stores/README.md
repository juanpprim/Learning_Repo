# Feature Stores

## Objectives
- Understand the training/serving skew problem a feature store solves.
- Define feature definitions, entities, and feature views with Feast.
- Materialize features to an online store and fetch them at low latency for serving.
- Retrieve point-in-time-correct historical features for training.

## Key concepts

> **Deep dive:** open [`key_concepts.html`](key_concepts.html) in a browser for animated explanations of each concept below.
- Offline store (for training, historical/batch) vs. online store (for serving, low-latency).
- Entities, feature views, point-in-time joins (avoiding label leakage).
- Materialization: pushing offline feature data into the online store.
- Feature reuse across teams/models as the core value proposition.

## Resources
- Feast docs: https://docs.feast.dev/
- Feast quickstart tutorial: https://docs.feast.dev/getting-started/quickstart

## Checklist
- [ ] Install Feast and initialize a feature repo (`feast init`).
- [ ] Define an entity and a feature view over a small local dataset (parquet/CSV).
- [ ] Run `feast apply` and `feast materialize` to populate the online store (SQLite is fine).
- [ ] Fetch online features for a given entity key via the Feast SDK.
- [ ] Fetch point-in-time-correct historical features for training and compare
      against a naive (leaky) join.

## Mini-project
Take a dataset with a timestamp column, build a Feast feature repo around it,
materialize to an online store, and demonstrate both online feature retrieval
(serving-time) and point-in-time historical retrieval (training-time) from the
same feature definitions.
