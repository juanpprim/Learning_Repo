# Learning Repo

A hands-on learning workspace for deep-diving into technologies adjacent to
(and beyond) core data science. Each top-level folder is a **track**; each
track contains **subtopics**, and every subtopic follows the same pattern:

```
<track>/<subtopic>/
  README.md           # objectives, key concepts, resources, checklist, mini-project
  key_concepts.html   # animated deep-dive on the key concepts — open in a browser
  notebooks/          # completed walkthrough notebook(s) to run and extend
                      # (or a src/ starter script for non-notebook topics)
  requirements.txt    # key libraries for that subtopic
```

Work through a subtopic by reading its README, ticking off the checklist as
you go, running/extending the starter notebook or script, and finishing with
the mini-project.

## Tracks

| Track | Focus | Why |
|---|---|---|
| [`mlops-production-ml/`](mlops-production-ml/) | Experiment tracking, model serving, CI/CD for ML, monitoring, feature stores | Closest to existing DS skills — closes the "model in a notebook" -> "model in production" gap |
| [`data-engineering-at-scale/`](data-engineering-at-scale/) | Spark, streaming (Kafka), orchestration (Airflow), dbt, cloud warehouses | High leverage for a senior DS — most real-world data problems are engineering problems first |
| [`parallel-distributed-processing/`](parallel-distributed-processing/) | Python concurrency, Dask/Ray, GPU parallelism, distributed training | Performance/scale skills that cut across MLOps and data engineering |
| [`game-development/`](game-development/) | Pygame basics, Godot intro, game AI & procedural generation | Deliberate stretch track — general programming/architecture practice outside data pipelines |
| [`app-development/`](app-development/) | FastAPI backend, React frontend, full-stack capstone | Ties the other tracks together by shipping a usable app end-to-end |

## Suggested order

1. **mlops-production-ml** and **data-engineering-at-scale** first — highest
   immediate leverage given 8 years of DS experience, and they reuse existing
   intuition about data and models.
2. **parallel-distributed-processing** next — deepens both of the above.
3. **game-development** and **app-development** last, as the "new territory"
   stretch tracks. The `full-stack-capstone-project` in `app-development` is
   designed to plug in a model or pipeline from an earlier track.

There's no strict requirement to go in order — pick whatever keeps you
motivated. The checklists in each subtopic README are the real unit of
progress tracking.
