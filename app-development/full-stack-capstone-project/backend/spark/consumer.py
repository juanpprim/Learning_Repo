"""Spark Structured Streaming prediction consumer (Tier B).

Reads JSON requests from `prediction-requests`, predicts with the SAME
registered MLflow models the direct path uses (models:/<name>@production),
writes each result to Postgres (where the waiting gateway finds it) and
emits a copy to `prediction-results`.

Deliberately a STATELESS map job — no windows, no watermarks — so the
streaming concepts stay separable (stateful analytics is a future improvement).

Runs inside the spark-consumer container (see spark/Dockerfile):
    spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.4 consumer.py
"""

import json
import os

import mlflow.pyfunc
import pandas as pd
import psycopg2
from confluent_kafka import Producer
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import IntegerType, StringType, StructField, StructType

BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+psycopg2://capstone:capstone@localhost:5432/capstone"
)
MLFLOW_URI = os.environ.get("MLFLOW_TRACKING_URI", "http://localhost:5000")

# The JSON shape produced by StreamingPredictor (app/serving/streaming.py).
FEATURES_SCHEMA = StructType(
    [
        StructField("area", IntegerType()),
        StructField("bedrooms", IntegerType()),
        StructField("bathrooms", IntegerType()),
        StructField("stories", IntegerType()),
        StructField("mainroad", StringType()),          # JSON bools arrive fine as strings
        StructField("guestroom", StringType()),
        StructField("basement", StringType()),
        StructField("hotwaterheating", StringType()),
        StructField("airconditioning", StringType()),
        StructField("parking", IntegerType()),
        StructField("prefarea", StringType()),
        StructField("furnishingstatus", StringType()),
    ]
)
MESSAGE_SCHEMA = StructType(
    [
        StructField("request_id", StringType()),
        StructField("model", StringType()),
        StructField("features", FEATURES_SCHEMA),
    ]
)

YESNO_COLS = ["mainroad", "guestroom", "basement", "hotwaterheating", "airconditioning", "prefarea"]

# Caches live per executor process — models load once, then serve every batch.
_models: dict = {}
_producer: Producer | None = None


def load_model(name: str):
    if name not in _models:
        mlflow.set_tracking_uri(MLFLOW_URI)
        _models[name] = mlflow.pyfunc.load_model(f"models:/{name}@production")
    return _models[name]


def get_producer() -> Producer:
    global _producer
    if _producer is None:
        _producer = Producer({"bootstrap.servers": BOOTSTRAP})
    return _producer


def to_training_frame(features: dict) -> pd.DataFrame:
    """Reshape a request's features into the format the pipelines were trained on
    (bools as 'yes'/'no' strings — mirrors HouseFeatures.to_frame())."""
    row = dict(features)
    for c in YESNO_COLS:
        v = row[c]
        row[c] = "yes" if str(v).lower() in ("true", "yes", "1") else "no"
    return pd.DataFrame([row])


def process_batch(batch_df, batch_id: int) -> None:
    """Handle one micro-batch: predict every request, write DB + results topic.

    collect() is fine here: micro-batches are small (single predictions), and
    it keeps the code a readable straight line instead of UDF gymnastics.
    """
    rows = batch_df.collect()
    if not rows:
        return

    # psycopg2 wants a plain DSN, not SQLAlchemy's dialect prefix.
    conn = psycopg2.connect(DATABASE_URL.replace("postgresql+psycopg2://", "postgresql://"))
    producer = get_producer()

    with conn, conn.cursor() as cur:
        for r in rows:
            features = r.features.asDict()
            price = float(load_model(r.model).predict(to_training_frame(features))[0])

            # The gateway is short-polling for exactly this row (by request_id).
            cur.execute(
                """
                INSERT INTO predictions
                    (created_at, request_id, model, serving_mode, features,
                     predicted_price, latency_ms)
                VALUES (now(), %s, %s, 'streaming', %s, %s, 0)
                """,
                (r.request_id, r.model, json.dumps(features), price),
            )

            # Also publish downstream — feeds lag metrics and future consumers.
            producer.produce(
                "prediction-results",
                key=r.request_id,
                value=json.dumps({"request_id": r.request_id, "predicted_price": price}),
            )
    producer.flush(5)
    conn.close()
    print(f"batch {batch_id}: served {len(rows)} prediction(s)")


def main() -> None:
    spark = (
        SparkSession.builder.appName("prediction-consumer")
        # Expose Spark's own metrics for Prometheus (scraped on :4040).
        .config("spark.ui.prometheus.enabled", "true")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")

    requests = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", BOOTSTRAP)
        .option("subscribe", "prediction-requests")
        .option("startingOffsets", "latest")
        .load()
        # Kafka gives us bytes; parse value -> typed columns.
        .select(from_json(col("value").cast("string"), MESSAGE_SCHEMA).alias("msg"))
        .select("msg.*")
    )

    query = requests.writeStream.foreachBatch(process_batch).start()
    print("prediction consumer running — waiting for requests…")
    query.awaitTermination()


if __name__ == "__main__":
    main()
