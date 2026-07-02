# Cloud Data Warehouses (BigQuery / Snowflake patterns)

## Objectives
- Understand columnar, MPP (massively parallel processing) warehouse architecture
  and why it differs from row-store OLTP databases.
- Write and optimize analytical SQL: window functions, CTEs, clustering/partitioning.
- Reason about cost models (bytes scanned, credits/compute) and how query design
  affects cost.

## Key concepts
- Storage/compute separation; partitioning and clustering to prune scanned data.
- Window functions (`ROW_NUMBER`, `LAG/LEAD`, running aggregates) for analytics.
- Materialized views vs. scheduled queries for pre-aggregation.
- Cost control: dry-run query cost estimates, partition pruning, avoiding `SELECT *`.

## Resources
- BigQuery docs — free tier + sandbox: https://cloud.google.com/bigquery/docs/sandbox
- BigQuery docs — best practices for query performance: https://cloud.google.com/bigquery/docs/best-practices-performance-overview
- Snowflake docs (if preferred over BigQuery): https://docs.snowflake.com/

## Checklist
- [ ] Load a public dataset into BigQuery sandbox (no credit card required) or
      a local DuckDB stand-in if avoiding cloud accounts for now.
- [ ] Write a query using window functions for a running/rolling metric.
- [ ] Partition/cluster a table and compare bytes-scanned before/after on a
      filtered query.
- [ ] Estimate query cost with a dry run before executing.

## Mini-project
Pick a public BigQuery dataset (e.g. `bigquery-public-data`), write an
analytical query with window functions answering a concrete question, and
document the bytes-scanned / cost difference between a naive query and an
optimized (partition-pruned) version.
