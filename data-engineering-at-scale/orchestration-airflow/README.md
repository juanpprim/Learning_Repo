# Orchestration with Airflow

## Objectives
- Model a data pipeline as a DAG of tasks with explicit dependencies.
- Understand scheduling, retries, backfills, and the Airflow execution model
  (scheduler, workers, metadata DB).
- Use sensors/operators to wait on and trigger external systems.

## Key concepts
- DAG, task, operator (PythonOperator/BashOperator/etc.), task dependencies (`>>`).
- Scheduling intervals, `catchup`, and backfilling historical runs.
- Idempotency: why tasks must be safely re-runnable.
- XComs for passing small data between tasks (and why not to abuse them for big data).
- TaskFlow API (`@dag`, `@task`) vs. classic operator syntax.

## Resources
- Airflow docs — concepts: https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/index.html
- Airflow docs — TaskFlow tutorial: https://airflow.apache.org/docs/apache-airflow/stable/tutorial/taskflow.html

## Checklist
- [ ] Run Airflow locally (`docker compose` with the official quick-start, or
      `pip install apache-airflow` in a venv).
- [ ] Write a DAG with 3+ tasks with explicit dependencies (a small fan-out/fan-in shape).
- [ ] Add a retry policy and simulate a failing task to observe retry behavior.
- [ ] Use TaskFlow (`@task`) to pass data between tasks via XCom.
- [ ] Trigger a manual backfill for a past date range.

## Mini-project
Build a DAG that: extracts data from a local file/API, transforms it (reuse a
pandas/Spark step from another subtopic if useful), and loads it somewhere
(local Parquet or SQLite) — with retries and a sensor that waits for the
source file to exist before starting.
