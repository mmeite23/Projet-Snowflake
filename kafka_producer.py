import os
import json
import uuid
import time
import random
import signal
import logging
import sys
from datetime import datetime, timezone
from kafka import KafkaProducer
from dotenv import load_dotenv

# --- CONFIGURATION ---

load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Kafka Settings
TOPIC_NAME = os.getenv("KAFKA_TOPIC_NAME", "sales_events")
BOOTSTRAP_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVER", "redpanda:9092")

# Accept a comma-separated list and produce a list for kafka-python
BOOTSTRAP_SERVERS = [s.strip() for s in BOOTSTRAP_SERVER.split(",") if s.strip()]

# Random Data Generation
rng = random.Random()
rng.seed(42)  # Seed for reproducibility

CUSTOMER_IDS = list(range(1, 151))
PRODUCT_IDS = list(range(1001, 1051))
SALES_CHANNELS = ["E-com", "Boutique Paris", "Boutique Lyon", "Boutique Bordeaux"]

# --- EVENT GENERATION FUNCTIONS ---

def generate_order_created_event():
    """Event 1: Simulates a new customer order (ORDER_CREATED)."""
    event = {
        "event_type": "ORDER_CREATED",
        "order_line_id": str(uuid.uuid4()), 
        "customer_id": rng.choice(CUSTOMER_IDS),
        "product_id": rng.choice(PRODUCT_IDS),
        "quantity": rng.choices([1, 2, 3, 6], weights=[0.6, 0.25, 0.1, 0.05])[0],
        "event_ts": datetime.now(timezone.utc).isoformat(),
        "source_service": "ecom_api",
        "sales_channel": rng.choice(SALES_CHANNELS) # Correction précédente: Ajout de 'sales_channel'
    }
    return event

def generate_inventory_adjusted_event():
    """Event 2: Simulates a stock variation (INVENTORY_ADJUSTED)."""
    adjustment_type = rng.choices(
        ["REPLENISHMENT", "CORRECTION", "SPOILAGE"], 
        weights=[0.6, 0.3, 0.1]
    )[0]
    
    quantity_change = rng.randint(20, 150) if adjustment_type == "REPLENISHMENT" else rng.randint(-15, -1)
        
    event = {
        "event_type": "INVENTORY_ADJUSTED",
        "event_id": str(uuid.uuid4()),
        "product_id": rng.choice(PRODUCT_IDS),
        "quantity_change": quantity_change,
        "event_ts": datetime.now(timezone.utc).isoformat(),
        "source_service": "warehouse_management",
        "adjustment_type": adjustment_type # Correction précédente: Ajout de 'adjustment_type'
    }
    return event

# --- MAIN LOGIC ---

def run_producer():
    """Connects to Kafka and continuously sends events with graceful shutdown and callbacks."""
    logging.info(f"Connecting to Kafka at {BOOTSTRAP_SERVERS}")

    try:
        producer = KafkaProducer(
            bootstrap_servers=BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            retries=5,
            linger_ms=10
        )
    except Exception as e:
        logging.critical(f"Failed to create Kafka producer: {e}")
        return

    running = True

    def _shutdown(signum, frame):
        nonlocal running
        logging.warning(f"Signal {signum} received: shutting down producer...")
        running = False

    # Trap signals for graceful shutdown
    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    logging.info("Producer started. Generating events...")

    def on_send_success(record_metadata):
        logging.debug(f"Message delivered to {record_metadata.topic} partition={record_metadata.partition} offset={record_metadata.offset}")

    def on_send_error(excp):
        logging.error(f"Message delivery failed: {excp}")

    try:
        while running:
            if rng.random() < 0.7:
                event = generate_order_created_event()
                key = event['order_line_id']
            else:
                event = generate_inventory_adjusted_event()
                key = event['event_id']

            try:
                future = producer.send(
                    TOPIC_NAME,
                    key=key.encode('utf-8'),
                    value=event
                )
                # Attach callbacks to log success/failure
                future.add_callback(on_send_success)
                future.add_errback(on_send_error)
            except Exception as e:
                logging.exception(f"Exception while sending message: {e}")

            time.sleep(rng.uniform(0.1, 0.3))

    finally:
        logging.info("Flushing and closing producer...")
        try:
            producer.flush(timeout=10)
            producer.close()
        except Exception as e:
            logging.warning(f"Error while closing producer: {e}")
        logging.info("Producer stopped.")

if __name__ == "__main__":
    run_producer()