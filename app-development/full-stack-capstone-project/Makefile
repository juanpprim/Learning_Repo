# One-liners for every routine action — the README stays short and CI reuses
# these exact commands. Run `make <target>` from this directory.

COMPOSE = docker compose -f infra/docker-compose.yml

# ---------- setup ----------
install:            ## install backend deps (uv) + frontend deps (npm)
	cd backend && uv sync
	cd frontend && npm install

# ---------- infrastructure ----------
up:                 ## start Postgres + MLflow containers
	$(COMPOSE) up -d

down:               ## stop them (data volumes survive)
	$(COMPOSE) down

# ---------- data & models ----------
seed:               ## batch-load Housing.csv (or synthetic fallback) into Postgres
	cd backend && uv run python -m ml.seed_data

train:              ## train LinReg + LightGBM, register both @production in MLflow
	cd backend && uv run python -m ml.train

# ---------- run the app ----------
run-backend:        ## FastAPI on :8000 (direct mode by default)
	cd backend && uv run uvicorn app.main:app --reload --port 8000

run-frontend:       ## React dev server on :5173
	cd frontend && npm run dev

# ---------- quality ----------
lint:               ## ruff over the backend
	cd backend && uv run ruff check .

test:               ## all backend tests (integration ones need Docker)
	cd backend && uv run pytest -q

test-unit:          ## fast tests only, no Docker needed
	cd backend && uv run pytest -q -m "not integration"

# ---------- load study ----------
load:               ## 100-user Locust baseline against localhost:8000
	cd backend && uv run locust -f tests/load/locustfile.py \
		--host http://localhost:8000 --headless -u 100 -r 20 -t 60s \
		--csv ../docs/load/baseline-100u

.PHONY: install up down seed train run-backend run-frontend lint test test-unit load
