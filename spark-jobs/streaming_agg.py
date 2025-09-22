import os
import json
import time
import psycopg2
import logging
from confluent_kafka import Consumer
from datetime import datetime, timedelta
from collections import defaultdict

# Setup logging to file only
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('aggregator.log')
    ]
)
logger = logging.getLogger(__name__)

KAFKA = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9094")
TOPIC = os.getenv("KAFKA_TOPIC", "binance.trades")
PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")
PG_DB = os.getenv("POSTGRES_DB", "crypto")
PG_USER = os.getenv("POSTGRES_USER", "grafana")
PG_PWD = os.getenv("POSTGRES_PASSWORD", "secret")

print("=== Binance Streaming Aggregator ===")
print(f"Kafka: {KAFKA}")
print(f"Topic: {TOPIC}")
print(f"PostgreSQL: {PG_HOST}:{PG_PORT}/{PG_DB}")

# Kafka Consumer
consumer = Consumer({
    'bootstrap.servers': KAFKA,
    'group.id': 'binance-streaming-agg',
    'auto.offset.reset': 'latest'
})

consumer.subscribe([TOPIC])

# Helper functions
def get_window_start(trade_time_ms):
    """Get the start of the 1-minute window for a given trade time"""
    dt = datetime.fromtimestamp(trade_time_ms / 1000)
    return dt.replace(second=0, microsecond=0)

def get_window_end(window_start):
    """Get the end of the 1-minute window"""
    return window_start + timedelta(minutes=1)

def write_to_postgres(aggregated_data):
    """Write aggregated data to PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            database=PG_DB,
            user=PG_USER,
            password=PG_PWD
        )
        
        cursor = conn.cursor()
        
        for data in aggregated_data:
            insert_sql = """
            INSERT INTO kpi_symbol_1m 
            (window_start, window_end, symbol, trades, avg_price, vwap, volume, volatility, anomaly)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (window_start, symbol) DO UPDATE SET
                window_end = EXCLUDED.window_end,
                trades = EXCLUDED.trades,
                avg_price = EXCLUDED.avg_price,
                vwap = EXCLUDED.vwap,
                volume = EXCLUDED.volume,
                volatility = EXCLUDED.volatility,
                anomaly = EXCLUDED.anomaly,
                inserted_at = now()
            """
            
            cursor.execute(insert_sql, (
                data["window_start"],
                data["window_end"],
                data["symbol"],
                data["trades"],
                data["avg_price"],
                data["vwap"],
                data["volume"],
                data["volatility"],
                data["anomaly"]
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Successfully inserted {len(aggregated_data)} rows to PostgreSQL")
        
    except Exception as e:
        logger.error(f"Error writing to PostgreSQL: {e}")

# Main processing loop
print("[START] Starting streaming aggregator...")
print("[INFO] Processing data in 1-minute windows...")

# Buffer for current window data
current_window_data = defaultdict(lambda: defaultdict(list))
last_processed_window = None

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            logger.error(f"Consumer error: {msg.error()}")
            continue
        
        try:
            # Parse message
            data = json.loads(msg.value().decode('utf-8'))
            
            # Get current window
            trade_time = data["trade_time"]
            window_start = get_window_start(trade_time)
            
            # If we've moved to a new window, process the previous one
            if last_processed_window is not None and window_start > last_processed_window:
                # Process previous window
                aggregated_data = []
                
                for symbol, trades in current_window_data[last_processed_window].items():
                    if not trades:
                        continue
                    
                    # Calculate metrics
                    prices = [trade["price"] for trade in trades]
                    quantities = [trade["qty"] for trade in trades]
                    notional_values = [trade["price"] * trade["qty"] for trade in trades]
                    
                    trades_count = len(trades)
                    avg_price = sum(prices) / len(prices)
                    total_volume = sum(quantities)
                    total_notional = sum(notional_values)
                    vwap = total_notional / total_volume if total_volume > 0 else 0
                    
                    # Calculate volatility (standard deviation)
                    if len(prices) > 1:
                        mean_price = avg_price
                        variance = sum((p - mean_price) ** 2 for p in prices) / (len(prices) - 1)
                        volatility = variance ** 0.5
                    else:
                        volatility = 0
                    
                    # Calculate max change ratio
                    min_price = min(prices)
                    max_price = max(prices)
                    max_change_ratio = (max_price - min_price) / avg_price if avg_price > 0 else 0
                    
                    # Anomaly detection (price change > 3%)
                    anomaly = max_change_ratio > 0.03
                    
                    aggregated_data.append({
                        "window_start": last_processed_window,
                        "window_end": get_window_end(last_processed_window),
                        "symbol": symbol,
                        "trades": trades_count,
                        "avg_price": avg_price,
                        "vwap": vwap,
                        "volume": total_volume,
                        "volatility": volatility,
                        "anomaly": anomaly
                    })
                
                # Write to PostgreSQL
                if aggregated_data:
                    write_to_postgres(aggregated_data)
                
                # Clear processed window data
                if last_processed_window in current_window_data:
                    del current_window_data[last_processed_window]
            
            # Add current trade to current window
            current_window_data[window_start][data["symbol"]].append(data)
            last_processed_window = window_start
            
            # Log progress every 1000 messages (less frequent)
            if len(current_window_data[window_start][data["symbol"]]) % 1000 == 0:
                logger.info(f"{data['symbol']}: {len(current_window_data[window_start][data['symbol']])} trades in current window")
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            continue

except KeyboardInterrupt:
    print("\n[SHUTDOWN] Shutting down streaming aggregator...")
    consumer.close()
    print("[SUCCESS] Shutdown complete")