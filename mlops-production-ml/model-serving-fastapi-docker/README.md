# Model Serving with FastAPI + Docker

## Objectives
- Wrap a trained model in a FastAPI service with a `/predict` endpoint.
- Validate request/response schemas with Pydantic.
- Containerize the service with Docker so it runs anywhere.
- Understand sync vs. async serving and basic load/latency tradeoffs.

## Key concepts

> **Deep dive:** open [`key_concepts.html`](key_concepts.html) in a browser for animated explanations of each concept below.
- Pydantic models for request validation and response typing.
- Loading a model once at startup (not per-request).
- Dockerfile layering, `.dockerignore`, multi-stage builds for smaller images.
- Health check (`/health`) and readiness vs. liveness.
- Batch vs. real-time inference.

## Resources
- FastAPI docs: https://fastapi.tiangolo.com/
- Docker docs — Python guide: https://docs.docker.com/language/python/
- "Designing Machine Learning Systems" (Chip Huyen) — serving chapter, for concepts.

## Checklist
- [ ] Build a FastAPI app with a `/predict` endpoint backed by a trained model
      (reuse the model from `experiment-tracking-mlflow/` if handy).
- [ ] Add Pydantic request/response models and validate with bad input.
- [ ] Add a `/health` endpoint.
- [ ] Write a `Dockerfile`, build the image, and run the container locally.
- [ ] Load-test the endpoint with a simple script (e.g. `httpx`/`locust`) and
      note p50/p99 latency.

## Mini-project
Serve a model end-to-end: FastAPI app -> Dockerfile -> running container
that answers `curl -X POST localhost:8000/predict` with a real prediction.
Document the exact `docker build` / `docker run` commands in this README.
