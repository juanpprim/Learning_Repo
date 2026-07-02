# Backend API with FastAPI

## Objectives
- Build a real backend beyond a single endpoint: routing, request/response
  models, a database, and basic auth.
- Understand REST conventions (resource-based URLs, HTTP verbs, status codes).
- Add persistence with an ORM (SQLModel/SQLAlchemy) instead of in-memory state.

## Key concepts

> **Deep dive:** open [`key_concepts.html`](key_concepts.html) in a browser for animated explanations of each concept below.
- Path/query/body parameters and Pydantic models for validation.
- Dependency injection (`Depends`) for shared logic (DB sessions, auth).
- CRUD patterns and mapping them to REST routes.
- Basic auth: hashing passwords, issuing/verifying a JWT.
- Migrations (Alembic) for evolving a database schema safely.

## Resources
- FastAPI docs — Tutorial: https://fastapi.tiangolo.com/tutorial/
- FastAPI docs — SQL databases (SQLModel): https://fastapi.tiangolo.com/tutorial/sql-databases/
- FastAPI docs — Security/OAuth2 with JWT: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/

## Checklist
- [ ] Build CRUD routes for one resource (e.g. `/items`) backed by SQLite via SQLModel.
- [ ] Add request/response Pydantic models distinct from the DB model.
- [ ] Add a `/signup` and `/login` route that hashes passwords and issues a JWT.
- [ ] Protect a route with `Depends` requiring a valid JWT.
- [ ] Write a couple of `pytest` tests using FastAPI's `TestClient`.

## Mini-project
Build a small multi-resource API (e.g. a notes app or todo app) with auth,
persistence, and tests — this becomes the backend half of
`full-stack-capstone-project/`.
