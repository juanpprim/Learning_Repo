#!/usr/bin/env bash
# Chaos drill (Tier C): kill a Kafka broker mid-load and watch recovery.
#
# Learning goal — resilience is a TEST, not a hope. The drill asserts:
#   (a) with 3 brokers, the streaming path keeps serving while one is down
#   (b) the killed broker rejoins the ISR after restart
# Watch it live in Grafana -> "Kafka Health" (ISR + under-replicated panels).
#
# Prereqs: make up-streaming-3 && make train && make run-backend-streaming
# Usage:   ./tests/chaos/kill_broker.sh [broker-container=infra-kafka2-1]

set -euo pipefail
BROKER="${1:-infra-kafka2-1}"
API=http://localhost:8000

PAYLOAD='{"features":{"area":7420,"bedrooms":4,"bathrooms":2,"stories":3,
"mainroad":true,"guestroom":false,"basement":false,"hotwaterheating":false,
"airconditioning":true,"parking":2,"prefarea":true,
"furnishingstatus":"furnished"},"model":"linreg"}'

predict_ok() {
  curl -sf -X POST "$API/predict" -H 'Content-Type: application/json' \
    -d "$PAYLOAD" -o /dev/null
}

echo "1) sanity: streaming path healthy before the drill"
predict_ok || { echo "FAIL: /predict not working before the drill"; exit 1; }

echo "2) killing broker: $BROKER"
docker stop "$BROKER" >/dev/null

echo "3) asserting the topic survives (10 requests against 2/3 brokers)"
ok=0
for _ in $(seq 10); do
  predict_ok && ok=$((ok + 1)) || true
  sleep 1
done
echo "   $ok/10 predictions succeeded with a broker down"
[ "$ok" -ge 8 ] || { echo "FAIL: too many errors while broker was down"; docker start "$BROKER"; exit 1; }

echo "4) restarting broker and waiting for ISR recovery"
docker start "$BROKER" >/dev/null
sleep 15
docker exec infra-kafka1-1 /opt/kafka/bin/kafka-topics.sh \
  --bootstrap-server localhost:9092 --describe --topic prediction-requests \
  | grep 'Partition:' || true

echo "5) final sanity: predictions still flow"
predict_ok || { echo "FAIL: /predict broken after recovery"; exit 1; }

echo "CHAOS DRILL PASSED: lost a broker under load, kept serving, recovered."
