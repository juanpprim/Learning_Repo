# Distributed Compute with Dask / Ray

## Objectives
- Scale pandas-like DataFrame operations beyond a single machine's memory with Dask.
- Understand lazy task graphs and when to `.compute()`.
- Use Ray for general distributed Python (arbitrary function parallelism, actors).
- Recognize when distributed compute is worth the overhead vs. a single beefy machine.

## Key concepts
- Dask DataFrame/Array as chunked, lazy versions of pandas/NumPy.
- Task graphs and the Dask dashboard for visualizing execution.
- Ray tasks (`@ray.remote` functions) vs. actors (stateful remote objects).
- Partitioning strategy and its effect on parallelism/shuffle cost.
- When NOT to distribute: data that fits in memory, latency-sensitive small jobs.

## Resources
- Dask docs: https://docs.dask.org/en/stable/
- Dask DataFrame best practices: https://docs.dask.org/en/stable/dataframe-best-practices.html
- Ray docs — Core concepts: https://docs.ray.io/en/latest/ray-core/walkthrough.html

## Checklist
- [ ] Load a dataset larger than comfortable pandas memory as a Dask DataFrame
      and run groupby/aggregate operations.
- [ ] Open the Dask dashboard and watch a task graph execute.
- [ ] Convert a CPU-bound function into a Ray remote task and run many in parallel.
- [ ] Build a small Ray actor that holds state across calls (e.g. a counter or cache).
- [ ] Compare wall-clock time: single-process pandas vs. Dask vs. Ray for the
      same workload.

## Mini-project
Take a dataset too large to comfortably fit in memory (or artificially chunk
a smaller one), process it with both Dask DataFrame and a hand-rolled Ray
task-based approach, and compare code complexity + performance in this README.
