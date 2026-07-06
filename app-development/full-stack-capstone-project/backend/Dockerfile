# Multi-stage build for the FastAPI gateway (Tier C).
# Stage 1 resolves/installs dependencies with uv; stage 2 is a slim runtime
# that only carries the virtualenv and the app code — no compilers, no uv.

# ---------- stage 1: builder ----------
FROM python:3.12-slim-bookworm AS builder

# uv is a single static binary — copy it in instead of pip-installing it.
COPY --from=ghcr.io/astral-sh/uv:0.9.27 /uv /usr/local/bin/uv

WORKDIR /app
# Dependency files first: this layer only rebuilds when deps change,
# not on every code edit (classic Docker cache trick).
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# ---------- stage 2: runtime ----------
FROM python:3.12-slim-bookworm

# libgomp1 = OpenMP, required by LightGBM's native library.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /app/.venv .venv
COPY app ./app
COPY ml ./ml

# The venv's binaries (uvicorn, python) come first on PATH.
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
