# Spark Fundamentals (PySpark)

## Objectives
- Understand Spark's distributed execution model: driver, executors, partitions,
  lazy evaluation, DAGs.
- Manipulate large-ish datasets with the DataFrame API (not RDDs, unless comparing).
- Recognize and fix common performance issues: shuffles, skew, wrong partitioning.

## Key concepts

> **Deep dive:** open [`key_concepts.html`](key_concepts.html) in a browser for animated explanations of each concept below.
- Lazy transformations vs. actions (`.filter()` vs. `.count()`).
- Partitions and shuffles; `repartition` vs. `coalesce`.
- Joins: broadcast join vs. shuffle join, and when Spark picks each.
- Catalyst optimizer / `.explain()` to read a query plan.
- Reading/writing Parquet vs. CSV and why columnar formats matter at scale.

## Resources
- Spark docs — Structured API guide: https://spark.apache.org/docs/latest/sql-programming-guide.html
- "Learning Spark, 2nd Edition" (O'Reilly, free chapters online).
- Databricks Spark tutorials: https://www.databricks.com/spark/getting-started-with-apache-spark

## Checklist
- [ ] Run a local PySpark session (`SparkSession.builder.master("local[*]")`).
- [ ] Load a CSV/Parquet dataset and perform filter/groupBy/agg operations.
- [ ] Read a `.explain()` plan and identify a shuffle.
- [ ] Force a skewed join on purpose, observe slow stage, then fix with a
      broadcast join or salting.
- [ ] Write the result out as partitioned Parquet.

## Mini-project
Take a multi-million-row public dataset (e.g. NYC taxi trips), do a non-trivial
aggregation + join in PySpark, and write a short note comparing runtime/plan
before and after an optimization (broadcast join, repartition, caching).
