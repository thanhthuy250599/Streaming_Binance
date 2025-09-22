import asyncio, os, signal
import websockets
from confluent_kafka import Producer
import orjson  # đừng alias thành json để tránh nhầm
import logging

# Setup logging to file only
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('producer.log')
    ]
)
logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9094")
TOPIC = os.getenv("KAFKA_TOPIC", "binance.trades")
SYMBOLS = [s.strip().lower() for s in os.getenv("BINANCE_SYMBOLS", "btcusdt,ethusdt").split(",")]
STREAMS = "/".join(f"{s}@trade" for s in SYMBOLS)
WS_URL = f"wss://stream.binance.com:9443/stream?streams={STREAMS}"

producer = Producer({"bootstrap.servers": KAFKA_BOOTSTRAP})

running = True

def delivery(err, msg):
    if err:
        logger.error(f"Delivery failed: {err}")
#    else:
        # In thêm thông tin để biết là có gửi thành công
#        logger.info(f"Delivery ok: {msg.topic()} [{msg.partition()}] @ {msg.offset()}")

def shutdown(*_):
    global running
    running = False
    print("Shutting down...")

async def run():
    global running
    print("KAFKA_BOOTSTRAP_SERVERS =", KAFKA_BOOTSTRAP)
    print("TOPIC =", TOPIC)
    print("SYMBOLS =", SYMBOLS)
    while running:
        try:
            async with websockets.connect(WS_URL, ping_interval=15, ping_timeout=20) as ws:
                print(f"Connected to {WS_URL}")
                print("Waiting for messages...")
                message_count = 0
                async for message in ws:
                    message_count += 1
                    if message_count % 1000 == 0:
                        logger.info(f"Received {message_count} messages...")
                    # message là str -> orjson.loads cần bytes
                    try:
                        m = orjson.loads(message.encode("utf-8"))
                    except Exception as e:
                        logger.error(f"JSON parse error: {e}, raw: {message[:200]}")
                        continue

                    d = m.get("data") or {}
                    if not d:
                        continue

                    try:
                        event = {
                            "symbol": d.get("s"),
                            "price": float(d.get("p")),
                            "qty": float(d.get("q")),
                            "trade_time": int(d.get("T")),
                            "is_buyer_maker": bool(d.get("m")),
                            "trade_id": int(d.get("t")),
                        }
                    except Exception as e:
                        logger.error(f"Field casting error: {e}, data: {d}")
                        continue

                    payload = orjson.dumps(event)  # bytes, OK cho confluent_kafka
                    key = (event["symbol"] or "").encode()

                    try:
                        producer.produce(
                            TOPIC,
                            key=key,
                            value=payload,
                            callback=delivery,
                        )
                        if message_count % 1000 == 0:
                            logger.info(f"Sent message {message_count} to Kafka: {event['symbol']} @ {event['price']}")
                    except BufferError:
                        # hàng đợi đầy: cho Kafka "xả" bớt callback rồi thử lại
                        producer.poll(0.5)
                        producer.produce(TOPIC, key=key, value=payload, callback=delivery)
                    # kích hoạt callback delivery
                    producer.poll(0)
        except Exception as e:
            logger.error(f"WebSocket error, reconnecting in 3s: {e}")
            await asyncio.sleep(3)
    # xả hết bản tin còn trong queue trước khi thoát
    try:
        producer.flush(5.0)
    except Exception:
        pass

if __name__ == "__main__":
    signal.signal(signal.SIGINT, shutdown)
    # SIGTERM có thể không được gửi trong Git Bash, nhưng để đây vẫn tốt
    try:
        signal.signal(signal.SIGTERM, shutdown)
    except Exception:
        pass
    asyncio.run(run())
