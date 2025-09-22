#!/usr/bin/env bash
set -euo pipefail

echo "[STOP] Stopping Binance Streaming Project..."

# Stop Python processes using PID files if they exist
if [ -f "producer.pid" ]; then
    PRODUCER_PID=$(cat producer.pid)
    echo "[STOP] Stopping Producer (PID: $PRODUCER_PID)..."
    kill "$PRODUCER_PID" 2>/dev/null || true
    rm -f producer.pid
fi

if [ -f "aggregator.pid" ]; then
    AGGREGATOR_PID=$(cat aggregator.pid)
    echo "[STOP] Stopping Aggregator (PID: $AGGREGATOR_PID)..."
    kill "$AGGREGATOR_PID" 2>/dev/null || true
    rm -f aggregator.pid
fi

# Fallback: stop by process name
echo "[STOP] Stopping any remaining processes..."
pkill -f "binance_ws_to_kafka.py" || true
pkill -f "streaming_agg.py" || true

# Stop Docker containers
echo "[DOCKER] Stopping Docker containers..."
docker compose down

echo "[SUCCESS] All services stopped successfully!"
echo ""
echo "[CLEANUP] To clean up completely:"
echo "  - Remove virtual environment: rm -rf .venv"
echo "  - Remove logs: rm -f producer.log aggregator.log"
echo "  - Remove checkpoint data: rm -rf chk/"
