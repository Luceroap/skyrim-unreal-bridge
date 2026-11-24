#!/usr/bin/env bash
set -u

ROOT="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$ROOT" || exit 1

MODEL="qwen3:14b-gpu"
BASE_URL="${HOMELAB_QWEN_URL:-http://127.0.0.1:11434/v1}"

echo "SkyBridge homelab worker"
echo "project: $ROOT"
echo "server:  $BASE_URL"
echo "model:   $MODEL"
echo "stop:    touch notes/STOP_HOMELAB"

while [ ! -f notes/STOP_HOMELAB ]; do
    python3 run_homelab_worker_linux.py \
        --base-url "$BASE_URL" \
        --model "$MODEL" \
        --worker homelab \
        --kinds H,K,M,X,N,T,Y,U \
        --cap 4500 \
        --timeout-min 4
    [ -f notes/STOP_HOMELAB ] && break
    echo "Worker stopped; retrying in 10 minutes."
    sleep 600
done

echo "Homelab worker stopped."
