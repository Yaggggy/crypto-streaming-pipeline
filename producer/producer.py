import websocket
import json
import os
from dotenv import load_dotenv
from confluent_kafka import Producer

# Load environment variables
load_dotenv()

# --- Kafka Configuration ---
conf = {
    'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS'),
    'client.id': 'crypto-producer',
    'acks': 'all'  # 'all' ensures the broker confirms receipt (Reliability)
}

# Initialize the Producer
producer = Producer(conf)
topic = os.getenv('KAFKA_TOPIC_RAW_TRADES')

def delivery_report(err, msg):
    """Callback: Called once for each message to check if it was delivered."""
    if err is not None:
        print(f"❌ Message delivery failed: {err}")
    else:
        # We print purely for verification. In production, you'd log this silently.
        print(f"✅ Delivered to {msg.topic()} [{msg.partition()}]")

def on_message(ws, message):
    data = json.loads(message)
    
    if data.get('type') == 'match':
        # Construct the clean data payload
        trade_data = {
            "trade_id": data.get("trade_id"),
            "product_id": data.get("product_id"),
            "price": float(data.get("price")),
            "size": float(data.get("size")),
            "side": data.get("side"),
            "time": data.get("time")
        }
        
        # Serialize to JSON string and send to Kafka
        # poll(0) checks for delivery callbacks from previous messages
        producer.poll(0)
        
        producer.produce(
            topic, 
            key=data.get("product_id"), # Using product_id as key ensures ordering
            value=json.dumps(trade_data), 
            callback=delivery_report
        )

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("### Connection Closed ###")
    producer.flush() # Ensure all buffered messages are sent before exiting

def on_open(ws):
    print("--- Connected to Coinbase: Streaming to Kafka ---")
    subscribe_msg = {
        "type": "subscribe",
        "channels": [{"name": "matches", "product_ids": ["BTC-USD"]}]
    }
    ws.send(json.dumps(subscribe_msg))

if __name__ == "__main__":
    ws_url = os.getenv("COINBASE_WS_URL")
    ws = websocket.WebSocketApp(
        ws_url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()