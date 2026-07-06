# Spark Structured Streaming consumer image.
#
# Built FROM python:3.12 (not a Spark image) so the Python libs match the
# backend exactly — the sklearn/LightGBM pickles were written by these
# versions and must be read by the same ones. Java is added for Spark itself.
#
# Build context is backend/ (see the compose files):
#   docker compose -f ... build spark-consumer

# bookworm pin: Debian 13 (trixie) dropped openjdk-17, which Spark 3.5 needs.
FROM python:3.12-slim-bookworm

# Spark needs a JVM (17 is the safest choice for Spark 3.5);
# libgomp1 is OpenMP, needed by LightGBM's native library at runtime.
RUN apt-get update \
    && apt-get install -y --no-install-recommends openjdk-17-jre-headless libgomp1 \
    && rm -rf /var/lib/apt/lists/*
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64

# Pinned to the SAME versions as backend/uv.lock (pickle compatibility).
RUN pip install --no-cache-dir \
    pyspark==3.5.4 \
    mlflow==3.14.0 \
    scikit-learn==1.9.0 \
    lightgbm==4.6.0 \
    pandas==2.3.3 \
    numpy==2.5.1 \
    psycopg2-binary==2.9.12 \
    confluent-kafka==2.6.1

WORKDIR /opt/consumer
COPY spark/consumer.py .

# Warm the ivy cache at BUILD time so the Kafka connector jars don't need
# downloading on every container start.
RUN python - <<'EOF'
from pyspark.sql import SparkSession
spark = (SparkSession.builder
         .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.4")
         .master("local[1]").appName("warmup").getOrCreate())
spark.stop()
EOF

# The three metrics confs expose driver metrics at :4040/metrics/prometheus
# (spark.ui.prometheus.enabled alone only covers executor metrics).
CMD ["spark-submit", \
     "--master", "local[2]", \
     "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.4", \
     "--conf", "spark.ui.prometheus.enabled=true", \
     "--conf", "spark.metrics.conf.*.sink.prometheusServlet.class=org.apache.spark.metrics.sink.PrometheusServlet", \
     "--conf", "spark.metrics.conf.*.sink.prometheusServlet.path=/metrics/prometheus", \
     "consumer.py"]
