"""Tier D2: the housing ML pipeline as an Airflow DAG.

seed -> train -> regression gate, with retries and explicit dependencies —
the same three commands the Makefile runs by hand, now orchestrated.

Runs inside the airflow container from infra/docker-compose.airflow.yml,
which mounts backend/ at /opt/capstone and pip-installs the ML deps.
(The folder is `airflow_dags/`, not `dags/`, because the repo root
.gitignore ignores every `dags/` directory.)

Manual trigger is the point for a learning repo; flip `schedule` to
"@daily" to see the scheduler take over.
"""

import pendulum
from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import dag

# Every task runs our existing modules, unchanged, from the mounted repo.
RUN = "cd /opt/capstone && python -m"


@dag(
    dag_id="housing_pipeline",
    schedule=None,  # manual trigger; set "@daily" to hand it to the scheduler
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    default_args={"retries": 2},  # transient DB/MLflow hiccups self-heal
    tags=["capstone"],
)
def housing_pipeline():
    seed = BashOperator(task_id="seed", bash_command=f"{RUN} ml.seed_data")
    train = BashOperator(task_id="train", bash_command=f"{RUN} ml.train")
    gate = BashOperator(task_id="regression_gate", bash_command=f"{RUN} ml.regression_gate")

    # The whole orchestration story in one line: order + implied data deps.
    seed >> train >> gate


housing_pipeline()
