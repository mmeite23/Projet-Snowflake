# kafka_consumer_snowflake.py - Les Caves d'Albert
# Production-ready Kafka Consumer with Prometheus metrics and Snowflake integration

import os
import json
import time
import signal
import logging
import pandas as pd
from kafka import KafkaConsumer, KafkaProducer
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from snowflake.sqlalchemy import URL
from dotenv import load_dotenv
from prometheus_client import Counter, Histogram, Gauge, start_http_server, Summary
from datetime import datetime

# --- 1. ENHANCED CONFIGURATION ---

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

load_dotenv()

# Kafka Settings
TOPIC_NAME = os.getenv("KAFKA_TOPIC_NAME", "sales_events")  # Updated for Les Caves d'Albert
DLQ_TOPIC_NAME = f"{TOPIC_NAME}_dlq"  # Dead-Letter Queue for invalid messages
BOOTSTRAP_SERVER = os.getenv("KAFKA_BOOTSTRAP_SERVER", "redpanda:9092")

# Snowflake Settings
SNOWFLAKE_USER = os.getenv('SNOWFLAKE_USER')
SNOWFLAKE_PASSWORD = os.getenv('SNOWFLAKE_PASSWORD')
SNOWFLAKE_ACCOUNT = os.getenv('SNOWFLAKE_ACCOUNT')
SNOWFLAKE_WAREHOUSE = os.getenv('SNOWFLAKE_WAREHOUSE')
SNOWFLAKE_DATABASE = os.getenv('SNOWFLAKE_DATABASE')
TARGET_SCHEMA = os.getenv('SNOWFLAKE_SCHEMA', 'RAW_DATA')

# Prometheus Metrics Port
METRICS_PORT = int(os.getenv('METRICS_PORT', '8000'))

# --- 2. PROMETHEUS METRICS DEFINITIONS ---

# Counters
events_consumed_total = Counter(
    'kafka_events_consumed_total',
    'Total number of events consumed from Kafka',
    ['event_type', 'status']  # labels: ORDER_CREATED/INVENTORY_ADJUSTED, success/failed
)

events_inserted_total = Counter(
    'snowflake_events_inserted_total',
    'Total number of events inserted into Snowflake',
    ['event_type']
)

dlq_messages_total = Counter(
    'dlq_messages_total',
    'Total number of messages sent to DLQ',
    ['error_type']
)

# Histograms
batch_size_histogram = Histogram(
    'batch_size_events',
    'Distribution of batch sizes',
    buckets=[10, 25, 50, 75, 100, 150, 200]
)

batch_processing_duration = Histogram(
    'batch_processing_duration_seconds',
    'Time taken to process and insert a batch',
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0]
)

snowflake_insert_duration = Histogram(
    'snowflake_insert_duration_seconds',
    'Time taken to insert data into Snowflake',
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Gauges
current_batch_size = Gauge(
    'current_batch_size',
    'Current number of events in the batch waiting to be processed'
)

kafka_lag = Gauge(
    'kafka_consumer_lag',
    'Current lag of the Kafka consumer',
    ['partition']
)

last_commit_timestamp = Gauge(
    'last_commit_timestamp',
    'Unix timestamp of the last successful commit'
)

# Summary
event_processing_summary = Summary(
    'event_processing_seconds',
    'Time spent processing individual events'
)

# --- 3. OPTIMIZED SNOWFLAKE SCHEMA FOR STREAMING (ELT APPROACH) ---

def setup_snowflake_schema(engine):
    """
    Creates tables for ingesting ALL raw events in JSON format.
    This is the cornerstone of the ELT approach. Transformation happens IN Snowflake.
    """
    RAW_TABLE_NAME = "RAW_EVENTS_STREAM"
    STAGING_TABLE = "stg_raw_events_stream"
    
    try:
        with engine.begin() as connection:
            # Use the database first
            connection.execute(text(f"USE DATABASE {SNOWFLAKE_DATABASE};"))
            
            # Create schema
            connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {TARGET_SCHEMA};"))
            
            # Use the schema
            connection.execute(text(f"USE SCHEMA {TARGET_SCHEMA};"))
            
            # Create main raw events table
            connection.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {TARGET_SCHEMA}.{RAW_TABLE_NAME} (
                    EVENT_TYPE VARCHAR(50),          -- Event type for quick filtering
                    PRODUCT_ID INTEGER,              -- Extracted for fast indexing
                    CUSTOMER_ID INTEGER,             -- Extracted for customer analytics
                    EVENT_METADATA OBJECT NOT NULL,  -- Kafka metadata (offset, partition)
                    EVENT_CONTENT VARIANT NOT NULL,  -- Raw JSON event data
                    INGESTION_TIME TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
                );
            """))
            
            # Create staging table (VARCHAR columns for pandas compatibility)
            connection.execute(text(f"""
                CREATE TABLE IF NOT EXISTS {TARGET_SCHEMA}.{STAGING_TABLE} (
                    EVENT_METADATA_V VARCHAR,
                    EVENT_CONTENT_V VARCHAR
                );
            """))
            
            # Verify staging table is empty at startup
            result = connection.execute(text(f"SELECT COUNT(*) as cnt FROM {TARGET_SCHEMA}.{STAGING_TABLE};"))
            staging_count = result.fetchone()[0]
            
            if staging_count > 0:
                logging.warning(f"⚠️  Staging table contains {staging_count} rows at startup. Cleaning...")
                connection.execute(text(f"TRUNCATE TABLE {TARGET_SCHEMA}.{STAGING_TABLE};"))
                logging.info(f"✅ Staging table cleaned successfully")
            
        logging.info(f"🍷 Snowflake schema and table '{RAW_TABLE_NAME}' ready for ingestion - Les Caves d'Albert")
        
    except Exception as e:
        logging.critical(f"❌ Critical error during Snowflake schema setup: {e}")
        raise

# --- 4. ROBUST INGESTION LOGIC WITH METRICS (ELT APPROACH) ---

def ingest_raw_events_batch(conn, batch):
    """
    Ingests a batch of raw events into the destination table.
    This function is simple, fast, and reliable with full metrics tracking.
    """
    if not batch:
        return
    
    start_time = time.time()
    batch_size = len(batch)
    
    # Track batch size
    batch_size_histogram.observe(batch_size)
    current_batch_size.set(batch_size)
    
    logging.info(f"📦 Processing batch of {batch_size} events...")

    df = pd.DataFrame(batch)
    
    # Extract key fields for faster querying
    df['EVENT_TYPE'] = df['EVENT_CONTENT'].apply(lambda x: x.get('event_type', 'UNKNOWN'))
    df['PRODUCT_ID'] = df['EVENT_CONTENT'].apply(lambda x: x.get('product_id', None))
    df['CUSTOMER_ID'] = df['EVENT_CONTENT'].apply(lambda x: x.get('customer_id', None))
    
    # Count events by type for metrics
    event_type_counts = df['EVENT_TYPE'].value_counts().to_dict()
    for event_type, count in event_type_counts.items():
        logging.info(f"  📊 {event_type}: {count} events")
    
    # Convert to JSON strings for staging table
    df['EVENT_CONTENT_JSON'] = df['EVENT_CONTENT'].apply(json.dumps)
    df['EVENT_METADATA_JSON'] = df['EVENT_METADATA'].apply(json.dumps)

    # Staging table setup
    STAGING_TABLE = "stg_raw_events_stream"
    full_staging = f"{TARGET_SCHEMA}.{STAGING_TABLE}"

    # Determine Engine for pandas.to_sql
    if isinstance(conn, Engine):
        engine = conn
        exec_conn = None
    else:
        engine = getattr(conn, 'engine', None)
        exec_conn = conn
    if engine is None:
        raise RuntimeError("Connection does not expose 'engine' required for pandas.to_sql")

    try:
        # Load data into staging table (VARCHAR columns)
        df_stg = df[['EVENT_METADATA_JSON', 'EVENT_CONTENT_JSON']].rename(columns={
            'EVENT_METADATA_JSON': 'EVENT_METADATA_V',
            'EVENT_CONTENT_JSON': 'EVENT_CONTENT_V'
        })

        staging_start = time.time()
        
        df_stg.to_sql(
            name=STAGING_TABLE,
            con=engine,
            schema=TARGET_SCHEMA,
            if_exists='append',
            index=False,
            method='multi',
            chunksize=1000
        )
        
        logging.info(f"  ✅ Loaded {len(df_stg)} rows into staging table")

        # Insert into final table with PARSE_JSON conversion and extracted fields
        insert_sql = text(f"""
            INSERT INTO {TARGET_SCHEMA}.RAW_EVENTS_STREAM 
                (EVENT_TYPE, PRODUCT_ID, CUSTOMER_ID, EVENT_METADATA, EVENT_CONTENT)
            SELECT 
                PARSE_JSON(EVENT_CONTENT_V):event_type::VARCHAR as EVENT_TYPE,
                PARSE_JSON(EVENT_CONTENT_V):product_id::INTEGER as PRODUCT_ID,
                PARSE_JSON(EVENT_CONTENT_V):customer_id::INTEGER as CUSTOMER_ID,
                PARSE_JSON(EVENT_METADATA_V) as EVENT_METADATA,
                PARSE_JSON(EVENT_CONTENT_V) as EVENT_CONTENT
            FROM {full_staging};
        """)

        # Execute operations
        if exec_conn is not None:
            exec_conn.execute(insert_sql)
            exec_conn.execute(text(f"TRUNCATE TABLE {full_staging};"))
        else:
            with engine.begin() as tx_conn:
                tx_conn.execute(insert_sql)
                tx_conn.execute(text(f"TRUNCATE TABLE {full_staging};"))
        
        # Record metrics
        snowflake_duration = time.time() - staging_start
        snowflake_insert_duration.observe(snowflake_duration)
        
        for event_type, count in event_type_counts.items():
            events_inserted_total.labels(event_type=event_type).inc(count)
        
        total_duration = time.time() - start_time
        batch_processing_duration.observe(total_duration)
        
        logging.info(f"  ⚡ Snowflake insert completed in {snowflake_duration:.2f}s")
        logging.info(f"  🎯 Total batch processing time: {total_duration:.2f}s")
        
        # Reset current batch size
        current_batch_size.set(0)
        
    except Exception as e:
        logging.error(f"❌ Error during batch ingestion: {e}")
        raise

# --- 5. MAIN CONSUMER LOOP (PRODUCTION-READY WITH METRICS) ---

# Global variable for graceful shutdown
running = True

def handle_shutdown(signum, frame):
    """Enables graceful shutdown on SIGINT (Ctrl+C) or SIGTERM."""
    global running
    logging.warning(f"⚠️  Signal {signum} received. Finishing current batch processing...")
    running = False

def validate_event_schema(event_content, event_type):
    """
    Validates that events contain required fields based on their type.
    Returns True if valid, False otherwise.
    """
    required_fields = {
        'ORDER_CREATED': ['order_line_id', 'customer_id', 'product_id', 'quantity'],
        'INVENTORY_ADJUSTED': ['event_id', 'product_id', 'quantity_change', 'adjustment_type']
    }
    
    if event_type not in required_fields:
        return True  # Unknown event types pass through
    
    for field in required_fields[event_type]:
        if field not in event_content:
            logging.warning(f"⚠️  Missing required field '{field}' in {event_type} event")
            return False
    
    return True

def main():
    """Main entry point of the consumer with Prometheus metrics."""
    global running
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)

    # Start Prometheus metrics server
    start_http_server(METRICS_PORT)
    logging.info(f"📊 Prometheus metrics server started on port {METRICS_PORT}")

    # Connect to services
    snowflake_engine = create_engine(URL(**{
        "user": SNOWFLAKE_USER, "password": SNOWFLAKE_PASSWORD, "account": SNOWFLAKE_ACCOUNT,
        "database": SNOWFLAKE_DATABASE, "warehouse": SNOWFLAKE_WAREHOUSE, "schema": TARGET_SCHEMA
    }))
    setup_snowflake_schema(snowflake_engine)

    # Producer for Dead-Letter Queue (DLQ)
    dlq_producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    consumer = KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=BOOTSTRAP_SERVER,
        auto_offset_reset='earliest',
        enable_auto_commit=False,
        group_id='snowflake-ingestion-les-caves-albert-v1',
        value_deserializer=lambda x: x.decode('utf-8')
    )

    logging.info(f"🍷 Les Caves d'Albert Consumer started. Listening to topic '{TOPIC_NAME}'")
    logging.info("=" * 80)

    batch = []
    last_commit = time.time()
    BATCH_SIZE = 100
    COMMIT_INTERVAL_SECONDS = 10
    
    # Event type counters for logging
    event_stats = {'ORDER_CREATED': 0, 'INVENTORY_ADJUSTED': 0, 'OTHER': 0, 'ERRORS': 0}

    try:
        while running:
            # Poll with timeout to avoid blocking indefinitely
            messages = consumer.poll(timeout_ms=1000, max_records=BATCH_SIZE)
            
            if not messages:
                # If no messages, check if we should commit current batch due to time elapsed
                if batch and (time.time() - last_commit > COMMIT_INTERVAL_SECONDS):
                    pass  # Commit will happen below
                else:
                    continue

            for topic_partition, msgs in messages.items():
                for msg in msgs:
                    with event_processing_summary.time():
                        try:
                            event_content = json.loads(msg.value)
                            event_type = event_content.get('event_type', 'UNKNOWN')
                            
                            # Validate event schema
                            if not validate_event_schema(event_content, event_type):
                                events_consumed_total.labels(event_type=event_type, status='invalid_schema').inc()
                                dlq_producer.send(DLQ_TOPIC_NAME, value={
                                    "raw_message": msg.value,
                                    "error": "InvalidSchema",
                                    "event_type": event_type,
                                    "offset": msg.offset
                                })
                                dlq_messages_total.labels(error_type='invalid_schema').inc()
                                event_stats['ERRORS'] += 1
                                continue
                            
                            event_metadata = {
                                "topic": msg.topic,
                                "partition": msg.partition,
                                "offset": msg.offset,
                                "timestamp_ms": msg.timestamp,
                                "key": msg.key.decode('utf-8') if msg.key else None
                            }
                            
                            batch.append({
                                "EVENT_METADATA": event_metadata,
                                "EVENT_CONTENT": event_content
                            })
                            
                            # Track event consumption
                            events_consumed_total.labels(event_type=event_type, status='success').inc()
                            
                            # Update stats
                            if event_type in event_stats:
                                event_stats[event_type] += 1
                            else:
                                event_stats['OTHER'] += 1
                            
                        except json.JSONDecodeError as e:
                            logging.error(f"❌ JSON decode error at offset {msg.offset}: {e}")
                            events_consumed_total.labels(event_type='UNKNOWN', status='json_error').inc()
                            dlq_producer.send(DLQ_TOPIC_NAME, value={
                                "raw_message": msg.value,
                                "error": f"JSONDecodeError: {str(e)}",
                                "offset": msg.offset
                            })
                            dlq_messages_total.labels(error_type='json_decode').inc()
                            event_stats['ERRORS'] += 1
                            continue
            
            # Commit condition: batch size or time interval reached
            if batch and (len(batch) >= BATCH_SIZE or time.time() - last_commit > COMMIT_INTERVAL_SECONDS):
                logging.info("=" * 80)
                with snowflake_engine.connect() as conn:
                    transaction = conn.begin()
                    try:
                        ingest_raw_events_batch(conn, batch)
                        transaction.commit()
                        consumer.commit()
                        
                        # Update metrics
                        last_commit_timestamp.set(time.time())
                        
                        # Log statistics
                        logging.info(f"✅ Batch committed successfully!")
                        logging.info(f"📈 Session stats - Orders: {event_stats['ORDER_CREATED']}, "
                                   f"Inventory: {event_stats['INVENTORY_ADJUSTED']}, "
                                   f"Other: {event_stats['OTHER']}, "
                                   f"Errors: {event_stats['ERRORS']}")
                        logging.info("=" * 80)
                        
                        batch = []
                        last_commit = time.time()
                        
                    except SQLAlchemyError as e:
                        logging.error(f"❌ Database error. Rolling back transaction: {e}")
                        transaction.rollback()
                        # Don't commit Kafka offset so messages can be reprocessed
    
    finally:
        logging.info("=" * 80)
        logging.info(f"🛑 Consumer shutdown initiated")
        logging.info(f"📊 Final stats - Orders: {event_stats['ORDER_CREATED']}, "
                   f"Inventory: {event_stats['INVENTORY_ADJUSTED']}, "
                   f"Other: {event_stats['OTHER']}, "
                   f"Errors: {event_stats['ERRORS']}")
        logging.info("🔄 Closing connections...")
        consumer.close()
        dlq_producer.close()
        snowflake_engine.dispose()
        logging.info("✅ Consumer stopped gracefully - Les Caves d'Albert")

if __name__ == "__main__":
    main()