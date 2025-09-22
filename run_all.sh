#!/usr/bin/env bash
set -euo pipefail

echo "[START] Starting Binance Streaming Project..."

# 1. Start infrastructure
echo "[DOCKER] Starting Docker containers..."
if ! docker compose ps >/dev/null 2>&1; then
  docker compose up -d
else
  docker compose up -d
fi

# Wait for containers to be ready
echo "[WAIT] Waiting for containers to be ready..."
sleep 10

# 2. Create Kafka topic if not exists
echo "[KAFKA] Creating Kafka topic..."
docker exec -i $(docker ps --filter "ancestor=confluentinc/cp-kafka:7.6.1" -q | head -n1) \
  kafka-topics --create --if-not-exists \
  --topic binance.trades \
  --bootstrap-server kafka:9092 \
  --replication-factor 1 \
  --partitions 6 || true

# 3. Setup Python environment
echo "[PYTHON] Setting up Python environment..."
if command -v python3 &>/dev/null; then
  PY=python3
else
  PY=python
fi

if [ -d ".venv" ]; then
    echo "[OK] Virtual environment already exists"
else
    $PY -m venv .venv
    echo "[CREATE] Created new virtual environment"
fi

# Use Python from virtual environment
if [ -f ".venv/Scripts/python.exe" ]; then
  # Windows
  PY=".venv/Scripts/python.exe"
elif [ -f ".venv/bin/python" ]; then
  # Linux / macOS / WSL
  PY=".venv/bin/python"
else
  echo "[ERROR] Virtual environment not found"
  exit 1
fi

# Install dependencies
echo "[INSTALL] Installing Python dependencies..."
$PY -m pip install -r producers/requirements.txt
$PY -m pip install psycopg2-binary

# 4. Start Producer
echo "[PRODUCER] Starting Binance WebSocket Producer..."
BINANCE_SYMBOLS="btcusdt,ethusdt" \
KAFKA_BOOTSTRAP_SERVERS="localhost:9094" \
PYTHONUNBUFFERED=1 \
nohup "$PY" producers/binance_ws_to_kafka.py > /dev/null 2>&1 &

PRODUCER_PID=$!
echo "[OK] Producer started (PID=$PRODUCER_PID)"

# Wait for producer to start
sleep 5

# Check if producer is running
if kill -0 "$PRODUCER_PID" 2>/dev/null; then
  echo "[OK] Producer is running (PID=$PRODUCER_PID)"
else
  echo "[ERROR] Producer failed to start"
  echo "[LOG] Producer logs:"
  tail -n 20 producer.log
  exit 1
fi

# 5. Start Streaming Aggregator
echo "[AGGREGATOR] Starting Streaming Aggregator..."
export KAFKA_BOOTSTRAP_SERVERS=localhost:9094
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=crypto
export POSTGRES_USER=grafana
export POSTGRES_PASSWORD=secret

nohup "$PY" spark-jobs/streaming_agg.py > /dev/null 2>&1 &

AGGREGATOR_PID=$!
echo "[OK] Streaming Aggregator started (PID=$AGGREGATOR_PID)"

# Wait for aggregator to start
sleep 5

# Check if aggregator is running
if kill -0 "$AGGREGATOR_PID" 2>/dev/null; then
  echo "[OK] Streaming Aggregator is running (PID=$AGGREGATOR_PID)"
else
  echo "[ERROR] Streaming Aggregator failed to start"
  echo "[LOG] Aggregator logs:"
  tail -n 20 aggregator.log
  exit 1
fi

# 6. Show status
echo ""
echo "[SUCCESS] All services started successfully!"
echo ""
echo "[STATUS] Service Status:"
echo "  - Producer (PID: $PRODUCER_PID): [RUNNING]"
echo "  - Aggregator (PID: $AGGREGATOR_PID): [RUNNING]"
echo "  - Kafka: [RUNNING]"
echo "  - PostgreSQL: [RUNNING]"
echo "  - Grafana: [RUNNING] (http://localhost:3000)"
echo ""
echo "[LOGS] Log files:"
echo "  - Producer: tail -f producer.log"
echo "  - Aggregator: tail -f aggregator.log"
echo ""
echo "[STOP] To stop all services:"
echo "  kill $PRODUCER_PID $AGGREGATOR_PID"
echo "  docker compose down"
echo ""

# Show recent logs
echo "[LOG] Recent Producer logs:"
tail -n 10 producer.log
echo ""
echo "[LOG] Recent Aggregator logs:"
tail -n 10 aggregator.log
echo ""

# Save PIDs to file for easy stopping
echo "$PRODUCER_PID" > producer.pid
echo "$AGGREGATOR_PID" > aggregator.pid

echo "[READY] All services are running in background."
echo "[INFO] Check logs manually if needed:"
echo "  - Producer: tail -f producer.log"
echo "  - Aggregator: tail -f aggregator.log"
echo ""
echo "[INFO] Use ./stop_all.sh to stop all services"
echo "[DONE] Script completed. Services running in background."