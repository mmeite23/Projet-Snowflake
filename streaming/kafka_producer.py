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

# Random Data Generation - Consistent with Data_generator_faker_docker
rng = random.Random()
rng.seed(42)  # Seed for reproducibility

# Les Caves d'Albert Configuration
CUSTOMER_IDS = list(range(1, 151))
PRODUCT_IDS = list(range(1000, 1050))  # Consistent with generator (1000-1049)
SALES_CHANNELS = ["E-com", "Boutique Paris", "Boutique Lyon", "Boutique Bordeaux"]

# Realistic wine data - Les Caves d'Albert 🍷
WINE_CATEGORIES = [
    ("🍷 Rouge", ["Merlot", "Cabernet Sauvignon", "Pinot Noir", "Syrah", "Malbec"]),
    ("🥂 Blanc", ["Chardonnay", "Sauvignon Blanc", "Riesling", "Viognier"]),
    ("🌸 Rosé", ["Grenache Rosé", "Syrah Rosé", "Cinsault Rosé"]),
    ("🍾 Effervescent", ["Champagne", "Crémant", "Prosecco"]),
    ("🥃 Spiritueux", ["Whisky", "Rhum", "Cognac", "Armagnac"]),
]

ADJECTIVES = ["Réserve", "Tradition", "Sélection", "Grande Cuvée", "Prestige", "Vieilles Vignes", "Édition Limitée"]
BOTTLE_SIZES = [0.375, 0.5, 0.75, 1.0, 1.5]

# Mapping product_id -> product details (simulated)
def get_product_name(product_id):
    """Generates a consistent product name based on ID"""
    rng_product = random.Random(product_id)  # Seed based on ID for consistency
    current_year = datetime.now().year
    category_emoji, grape_list = rng_product.choice(WINE_CATEGORIES)
    grape = rng_product.choice(grape_list)
    adj = rng_product.choice(ADJECTIVES)
    year = rng_product.randint(current_year - 15, current_year)
    return f"{grape} {year} – {adj}", category_emoji

def get_product_price(product_id):
    """Generates a consistent price based on ID"""
    rng_price = random.Random(product_id + 1000)
    category_emoji, _ = get_product_name(product_id)[1], None
    
    # Base price per category
    if "Rouge" in category_emoji:
        base = 18
    elif "Blanc" in category_emoji:
        base = 15
    elif "Rosé" in category_emoji:
        base = 12
    elif "Effervescent" in category_emoji:
        base = 30
    else:  # Spiritueux
        base = 45
    
    return round(rng_price.uniform(base * 0.7, base * 2), 2)

# --- EVENT GENERATION FUNCTIONS ---

def generate_order_created_event():
    """🛒 Event 1: Simulates a new customer order (ORDER_CREATED) - Les Caves d'Albert"""
    product_id = rng.choice(PRODUCT_IDS)
    product_name, category_emoji = get_product_name(product_id)
    quantity = rng.choices([1, 2, 3, 6], weights=[0.6, 0.25, 0.1, 0.05])[0]
    unit_price = get_product_price(product_id)
    total_price = round(quantity * unit_price, 2)
    customer_id = rng.choice(CUSTOMER_IDS)
    sales_channel = rng.choice(SALES_CHANNELS)
    bottle_size = rng.choice(BOTTLE_SIZES)
    
    # Apply discount (25% chance)
    discount = round(rng.uniform(0, 10), 2) if rng.random() < 0.25 else 0.0
    
    event = {
        "event_type": "ORDER_CREATED",
        "order_line_id": str(uuid.uuid4()),
        "customer_id": customer_id,
        "product_id": product_id,
        "product_name": product_name,
        "category": category_emoji,
        "quantity": quantity,
        "unit_price": unit_price,
        "total_price": total_price,
        "discount": discount,
        "bottle_size_l": bottle_size,
        "sales_channel": sales_channel,
        "event_ts": datetime.now(timezone.utc).isoformat(),
        "source_service": "ecom_api",
        "emoji": "🛒"
    }
    
    logging.info(f"🛒 ORDER_CREATED | Customer #{customer_id} | {category_emoji} {product_name} | Qty: {quantity} | Price: €{total_price} | Channel: {sales_channel}")
    return event

def generate_inventory_adjusted_event():
    """📦 Event 2: Simulates inventory variation (INVENTORY_ADJUSTED) - Les Caves d'Albert"""
    adjustment_type = rng.choices(
        ["REPLENISHMENT", "CORRECTION", "SPOILAGE"], 
        weights=[0.6, 0.3, 0.1]
    )[0]
    
    # Emojis based on adjustment type
    adjustment_emojis = {
        "REPLENISHMENT": "📦",  # Stock replenishment
        "CORRECTION": "✏️",      # Inventory correction
        "SPOILAGE": "❌"         # Breakage/Loss
    }
    
    product_id = rng.choice(PRODUCT_IDS)
    product_name, category_emoji = get_product_name(product_id)
    
    # Quantity logic based on type
    if adjustment_type == "REPLENISHMENT":
        quantity_change = rng.randint(20, 150)
    else:
        quantity_change = rng.randint(-15, -1)
    
    warehouse_location = rng.choice(["Entrepôt Paris", "Entrepôt Lyon", "Entrepôt Bordeaux", "Cave Centrale"])
    
    event = {
        "event_type": "INVENTORY_ADJUSTED",
        "event_id": str(uuid.uuid4()),
        "product_id": product_id,
        "product_name": product_name,
        "category": category_emoji,
        "quantity_change": quantity_change,
        "adjustment_type": adjustment_type,
        "warehouse_location": warehouse_location,
        "event_ts": datetime.now(timezone.utc).isoformat(),
        "source_service": "warehouse_management",
        "emoji": adjustment_emojis[adjustment_type]
    }
    
    sign = "+" if quantity_change > 0 else ""
    logging.info(f"{adjustment_emojis[adjustment_type]} INVENTORY_ADJUSTED | Product #{product_id} | {category_emoji} {product_name} | {sign}{quantity_change} units | Type: {adjustment_type} | {warehouse_location}")
    return event

# --- MAIN LOGIC ---

def run_producer():
    """🚀 Connects to Kafka and continuously sends events with graceful shutdown - Les Caves d'Albert"""
    logging.info(f"🔌 Connecting to Kafka at {BOOTSTRAP_SERVERS}")

    try:
        producer = KafkaProducer(
            bootstrap_servers=BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            retries=5,
            linger_ms=10
        )
    except Exception as e:
        logging.critical(f"❌ Failed to create Kafka producer: {e}")
        return

    running = True

    def _shutdown(signum, frame):
        nonlocal running
        logging.warning(f"⚠️  Signal {signum} received: shutting down producer...")
        running = False

    # Trap signals for graceful shutdown
    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    logging.info("🍷 Les Caves d'Albert Producer started. Generating events...")
    logging.info("=" * 80)

    def on_send_success(record_metadata):
        logging.debug(f"✅ Message delivered to {record_metadata.topic} partition={record_metadata.partition} offset={record_metadata.offset}")

    def on_send_error(excp):
        logging.error(f"❌ Message delivery failed: {excp}")

    try:
        event_count = 0
        while running:
            # 70% orders, 30% inventory adjustments
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
                
                event_count += 1
                
            except Exception as e:
                logging.exception(f"❌ Exception while sending message: {e}")

            time.sleep(rng.uniform(0.1, 0.3))

    finally:
        logging.info("=" * 80)
        logging.info(f"📊 Total events generated: {event_count}")
        logging.info("🔄 Flushing and closing producer...")
        try:
            producer.flush(timeout=10)
            producer.close()
        except Exception as e:
            logging.warning(f"⚠️  Error while closing producer: {e}")
        logging.info("🛑 Producer stopped - Les Caves d'Albert")

if __name__ == "__main__":
    run_producer()