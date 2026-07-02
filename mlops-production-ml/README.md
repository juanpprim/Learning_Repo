# MLOps & Production ML

Closing the gap between "model works in a notebook" and "model runs reliably
in production." Go through subtopics roughly in this order:

1. [`experiment-tracking-mlflow/`](experiment-tracking-mlflow/) — track params, metrics, and artifacts so experiments are reproducible.
2. [`model-serving-fastapi-docker/`](model-serving-fastapi-docker/) — package a trained model behind a real API.
3. [`ci-cd-for-ml/`](ci-cd-for-ml/) — automate testing/training/deployment on every change.
4. [`monitoring-observability/`](monitoring-observability/) — detect drift and failures after deployment.
5. [`feature-stores/`](feature-stores/) — share and reuse features consistently between training and serving.

Each subtopic is self-contained (README + starter notebook + requirements.txt).
