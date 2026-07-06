# One-liners for every routine action — the README stays short and CI reuses
# these exact commands. Run `make <target>` from this directory.

COMPOSE = docker compose -f infra/docker-compose.yml
# Full streaming stack = base + Kafka broker(s) + Prometheus/Grafana.
STREAM1 = $(COMPOSE) -f infra/docker-compose.kafka-1broker.yml -f infra/docker-compose.observability.yml
STREAM3 = $(COMPOSE) -f infra/docker-compose.kafka-3broker.yml -f infra/docker-compose.observability.yml

# ---------- setup ----------
install:            ## install backend deps (uv) + frontend deps (npm)
	cd backend && uv sync
	cd frontend && npm install

# ---------- infrastructure ----------
up:                 ## start Postgres + MLflow containers
	$(COMPOSE) up -d

down:               ## stop them (data volumes survive)
	$(COMPOSE) down

up-streaming:       ## Tier B: + Kafka (1 broker), Spark consumer, Prometheus, Grafana
	$(STREAM1) up -d --build

up-streaming-3:     ## Tier B: same but 3 Kafka brokers (replication study)
	$(STREAM3) up -d --build

down-streaming:     ## stop the whole streaming stack
	$(STREAM1) down --remove-orphans

up-full:            ## Tier C: EVERYTHING in containers (app + kafka + observability)
	$(STREAM1) -f infra/docker-compose.app.yml up -d --build

down-full:          ## stop the full containerized stack
	$(STREAM1) -f infra/docker-compose.app.yml down --remove-orphans

gate:               ## model-regression gate (same command CI runs)
	cd backend && uv run python -m ml.regression_gate

chaos:              ## kill a Kafka broker mid-flight (needs up-streaming-3)
	cd backend && ./tests/chaos/kill_broker.sh

# ---------- Tier C.5: Kubernetes + HPA (k3d) ----------
# Mind the 4-core host: run these alongside the 1-broker overlay, never 3-broker.
KUBECTL = PATH=$$HOME/.local/bin:$$PATH kubectl

k3d-up:             ## create the k3d cluster (gateway on :8000, ksm on :30080)
	PATH=$$HOME/.local/bin:$$PATH k3d cluster create capstone \
		-p "8000:80@loadbalancer" -p "30080:30080@server:0" --wait

k3d-deploy:         ## build+import the gateway image, apply all manifests
	docker build -t capstone-backend backend
	PATH=$$HOME/.local/bin:$$PATH k3d image import capstone-backend -c capstone
	$(KUBECTL) apply -f infra/k8s/
	$(KUBECTL) rollout status deployment/gateway --timeout=180s

k3d-status:         ## pods, HPA state, recent events
	$(KUBECTL) get pods,hpa,ingress
	$(KUBECTL) top pods 2>/dev/null || true

k3d-watch-hpa:      ## live view while a load sweep runs
	$(KUBECTL) get hpa gateway --watch

k3d-chaos:          ## delete a gateway pod mid-load; Service should reroute
	cd backend && ./tests/chaos/kill_pod.sh

k3d-down:           ## delete the cluster (compose stack untouched)
	PATH=$$HOME/.local/bin:$$PATH k3d cluster delete capstone

# ---------- Tier D ----------
amplify:            ## 545 rows -> 1M-row parquet (data/housing_amplified.parquet)
	cd backend && uv run python -m ml.amplify --rows 1000000

airflow-up:         ## Airflow standalone orchestrating seed -> train -> gate
	$(COMPOSE) -f infra/docker-compose.airflow.yml up -d

airflow-check:      ## DAG integrity: fail if any DAG has import errors
	docker compose -f infra/docker-compose.yml -f infra/docker-compose.airflow.yml \
		exec airflow airflow dags list-import-errors
	docker compose -f infra/docker-compose.yml -f infra/docker-compose.airflow.yml \
		exec airflow airflow dags list

airflow-run:        ## trigger the housing_pipeline DAG once
	# unpause first: DAGs start paused in a fresh metadata DB, and a
	# trigger on a paused DAG sits in "queued" forever.
	docker compose -f infra/docker-compose.yml -f infra/docker-compose.airflow.yml \
		exec airflow airflow dags unpause housing_pipeline
	docker compose -f infra/docker-compose.yml -f infra/docker-compose.airflow.yml \
		exec airflow airflow dags trigger housing_pipeline

# ---------- data & models ----------
seed:               ## batch-load Housing.csv (or synthetic fallback) into Postgres
	cd backend && uv run python -m ml.seed_data

train:              ## train LinReg + LightGBM, register both @production in MLflow
	cd backend && uv run python -m ml.train

# ---------- run the app ----------
# --host 0.0.0.0 so the Prometheus container can scrape the dev gateway
# through host.docker.internal.
run-backend:        ## FastAPI on :8000 (direct mode by default)
	cd backend && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-backend-streaming: ## FastAPI on :8000 in streaming mode (needs up-streaming)
	cd backend && SERVING_MODE=streaming uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

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

load-sweep:         ## 10/100 user sweep; NAME=direct or NAME=streaming labels the CSVs
	cd backend && for u in 10 100; do \
		uv run locust -f tests/load/locustfile.py --host http://localhost:8000 \
			--headless -u $$u -r 50 -t 30s --csv ../docs/load/$(NAME)-$${u}u --only-summary; \
	done

.PHONY: install up down up-streaming up-streaming-3 down-streaming up-full down-full \
	seed train gate chaos amplify airflow-up airflow-check airflow-run \
	run-backend run-backend-streaming run-frontend lint test test-unit load load-sweep
