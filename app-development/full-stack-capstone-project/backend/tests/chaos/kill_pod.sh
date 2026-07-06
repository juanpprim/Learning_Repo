#!/usr/bin/env bash
# Chaos drill (Tier C.5): delete a gateway pod and prove the Service reroutes.
#
# What k8s promises: the Deployment replaces the pod, the Service only sends
# traffic to READY pods (readiness probe), so callers see at most a blip.
#
# Prereqs: make k3d-up && make k3d-deploy (and the streaming compose stack up)
# Usage:   ./tests/chaos/kill_pod.sh

set -euo pipefail
export PATH="$HOME/.local/bin:$PATH"
API=http://localhost:8000

echo "1) sanity: gateway healthy through the Ingress"
curl -sf "$API/health" >/dev/null || { echo "FAIL: gateway not healthy"; exit 1; }

VICTIM=$(kubectl get pods -l app=gateway -o jsonpath='{.items[0].metadata.name}')
echo "2) deleting pod: $VICTIM"
kubectl delete pod "$VICTIM" --wait=false >/dev/null

echo "3) hammering /health while the pod dies and its replacement starts"
ok=0
for _ in $(seq 20); do
  curl -sf --max-time 2 "$API/health" >/dev/null && ok=$((ok + 1)) || true
  sleep 0.5
done
echo "   $ok/20 health checks succeeded during replacement"
[ "$ok" -ge 16 ] || { echo "FAIL: too many errors while the pod was replaced"; exit 1; }

echo "4) waiting for the Deployment to be fully restored"
kubectl rollout status deployment/gateway --timeout=120s >/dev/null
kubectl get pods -l app=gateway

echo "CHAOS DRILL PASSED: pod deleted, Service rerouted, Deployment self-healed."
