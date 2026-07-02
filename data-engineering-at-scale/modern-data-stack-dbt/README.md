# Modern Data Stack: dbt

## Objectives
- Write SQL-first transformations as version-controlled, testable dbt models.
- Understand the staging -> intermediate -> mart layering convention.
- Add data tests (uniqueness, not-null, relationships) and generate docs/lineage.

## Key concepts

> **Deep dive:** open [`key_concepts.html`](key_concepts.html) in a browser for animated explanations of each concept below.
- Models as `SELECT` statements; dbt compiles + runs them as views/tables.
- `ref()` and `source()` for building a dependency graph between models.
- Materializations: view, table, incremental, ephemeral.
- Built-in and custom generic tests (`unique`, `not_null`, `relationships`, `accepted_values`).
- `dbt docs generate` for auto-generated lineage graphs.

## Resources
- dbt docs — Quickstart: https://docs.getdbt.com/guides
- dbt docs — Best practices (layering): https://docs.getdbt.com/best-practices

## Checklist
- [ ] Set up a dbt project against a local DuckDB or SQLite database.
- [ ] Define a `staging` model that cleans/renames raw source columns.
- [ ] Build an `intermediate` and a `mart` model on top of it using `ref()`.
- [ ] Add at least 3 data tests and run `dbt test`.
- [ ] Generate and view the docs/lineage graph with `dbt docs generate && dbt docs serve`.

## Mini-project
Take a raw CSV dataset, load it into DuckDB, and build a small
staging -> intermediate -> mart dbt project on top of it with tests passing
and a lineage graph you can screenshot/describe in this README.
