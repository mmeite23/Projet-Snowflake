# 🍷 Kafka Consumer - Les Caves d'Albert - Production Ready

## 🎯 Overview

This is a **production-ready Kafka consumer** that ingests wine sales events from Kafka and stores them in Snowflake with full **Prometheus metrics** and **Grafana dashboards** for monitoring.

---

## ✨ Features Implemented

### ✅ Phase 1 - Critical Corrections
- [x] Fixed topic name to `sales_events` (matching producer)
- [x] All comments and logs in English with emojis
- [x] Enhanced staging table monitoring
- [x] Startup validation of staging table

### ✅ Phase 2 - Production Improvements
- [x] Metrics tracking by event type (ORDER_CREATED, INVENTORY_ADJUSTED)
- [x] Schema validation for events
- [x] Improved error handling with detailed DLQ
- [x] Performance metrics (batch processing time, Snowflake insert duration)
- [x] Session statistics logging

### ✅ Bonus - Prometheus & Grafana
- [x] Full Prometheus metrics integration
- [x] Grafana dashboard with 8 panels
- [x] Real-time monitoring of throughput, latency, errors
- [x] Docker Compose setup for easy deployment

---

## 📊 Prometheus Metrics

### Counters
| Metric | Description | Labels |
|--------|-------------|--------|
| `kafka_events_consumed_total` | Total events consumed from Kafka | `event_type`, `status` |
| `snowflake_events_inserted_total` | Total events inserted to Snowflake | `event_type` |
| `dlq_messages_total` | Total messages sent to DLQ | `error_type` |

### Histograms
| Metric | Description | Buckets |
|--------|-------------|---------|
| `batch_size_events` | Distribution of batch sizes | 10, 25, 50, 75, 100, 150, 200 |
| `batch_processing_duration_seconds` | Batch processing time | 0.1, 0.5, 1, 2.5, 5, 10, 30 |
| `snowflake_insert_duration_seconds` | Snowflake insert time | 0.1, 0.5, 1, 2.5, 5, 10 |

### Gauges
| Metric | Description |
|--------|-------------|
| `current_batch_size` | Current events in batch |
| `last_commit_timestamp` | Unix timestamp of last commit |

---

## 🗄️ Snowflake Schema

### Main Table: `RAW_EVENTS_STREAM`
```sql
CREATE TABLE RAW_EVENTS_STREAM (
    EVENT_TYPE VARCHAR(50),          -- Quick filtering: ORDER_CREATED, INVENTORY_ADJUSTED
    PRODUCT_ID INTEGER,              -- Fast product lookups
    CUSTOMER_ID INTEGER,             -- Customer analytics
    EVENT_METADATA OBJECT NOT NULL,  -- Kafka metadata (topic, partition, offset, timestamp)
    EVENT_CONTENT VARIANT NOT NULL,  -- Full raw JSON event
    INGESTION_TIME TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP()
);
```

### Staging Table: `stg_raw_events_stream`
```sql
CREATE TABLE stg_raw_events_stream (
    EVENT_METADATA_V VARCHAR,
    EVENT_CONTENT_V VARCHAR
);
```
**Note:** This table should ALWAYS be empty (auto-truncated after each batch).

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install kafka-python sqlalchemy snowflake-sqlalchemy pandas prometheus-client python-dotenv
```

### 2. Configure Environment Variables
Create a `.env` file:
```bash
# Kafka Configuration
KAFKA_TOPIC_NAME=sales_events
KAFKA_BOOTSTRAP_SERVER=redpanda:9092

# Snowflake Configuration
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_DATABASE=your_database
SNOWFLAKE_SCHEMA=RAW_DATA

# Metrics Configuration
METRICS_PORT=8000
```

### 3. Start Monitoring Stack (Prometheus + Grafana)
```bash
docker compose -f docker-compose-monitoring.yml up -d
```

Access:
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin123)

### 4. Run the Consumer
```bash
python kafka_consumer_snowflake.py
```

---

## 📈 Grafana Dashboard

The dashboard includes 8 panels:

1. **🛒 Events Consumed Rate** - Real-time ingestion rate by event type
2. **📊 Total Events Consumed** - Gauge showing total events processed
3. **📦 Current Batch Size** - Current number of events in batch
4. **⚡ Batch Processing Duration** - p50 and p95 latency for batches
5. **❄️ Snowflake Insert Duration** - Database insertion performance
6. **💾 Events Inserted to Snowflake** - Successful inserts per minute
7. **❌ DLQ Messages** - Error tracking by error type
8. **📋 Events Summary** - Detailed table breakdown by type and status

### Import Dashboard
1. Open Grafana at http://localhost:3000
2. Dashboard is auto-loaded via provisioning
3. Navigate to "Les Caves d'Albert - Kafka Consumer Metrics"

---

## 🔍 Monitoring & Alerts

### Key Metrics to Monitor

#### Performance
```promql
# Average batch processing time (last 5 minutes)
rate(batch_processing_duration_seconds_sum[5m]) / rate(batch_processing_duration_seconds_count[5m])

# 95th percentile Snowflake insert time
histogram_quantile(0.95, rate(snowflake_insert_duration_seconds_bucket[5m]))
```

#### Health
```promql
# Events consumed per second
rate(kafka_events_consumed_total{status="success"}[1m])

# Error rate
rate(kafka_events_consumed_total{status!="success"}[1m])

# DLQ message rate
rate(dlq_messages_total[5m])
```

#### Capacity
```promql
# Current batch utilization
current_batch_size / 100  # Assuming max batch size of 100
```

---

## 🛠️ Architecture

```
┌─────────────────┐
│  Kafka Topic    │
│ "sales_events"  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  Consumer Process       │
│  - Batch: 100 events    │
│  - Timeout: 10s         │
│  - Schema Validation    │
└────────┬────────────────┘
         │
         ├──────────────────────────┐
         │                          │
         ▼                          ▼
┌─────────────────┐      ┌──────────────────┐
│  DLQ Topic      │      │  Prometheus      │
│  (Errors)       │      │  Metrics :8000   │
└─────────────────┘      └────────┬─────────┘
                                  │
                                  ▼
         ┌────────────────────────────────┐
         │  Snowflake Warehouse           │
         │  ┌──────────────────────────┐  │
         │  │ stg_raw_events_stream    │  │
         │  │ (temp, always empty)     │  │
         │  └──────────┬───────────────┘  │
         │             │ PARSE_JSON        │
         │             ▼                   │
         │  ┌──────────────────────────┐  │
         │  │ RAW_EVENTS_STREAM        │  │
         │  │ - EVENT_TYPE             │  │
         │  │ - PRODUCT_ID             │  │
         │  │ - CUSTOMER_ID            │  │
         │  │ - EVENT_METADATA (OBJECT)│  │
         │  │ - EVENT_CONTENT (VARIANT)│  │
         │  └──────────────────────────┘  │
         └────────────────────────────────┘
                      │
                      ▼
              ┌──────────────┐
              │   Grafana    │
              │  Dashboard   │
              └──────────────┘
```

---

## 📊 Sample Logs

### Startup
```
2025-10-19 16:30:12 - INFO - 📊 Prometheus metrics server started on port 8000
2025-10-19 16:30:13 - INFO - 🍷 Snowflake schema and table 'RAW_EVENTS_STREAM' ready - Les Caves d'Albert
2025-10-19 16:30:13 - INFO - 🍷 Les Caves d'Albert Consumer started. Listening to topic 'sales_events'
2025-10-19 16:30:13 - INFO - ================================================================================
```

### Batch Processing
```
2025-10-19 16:30:45 - INFO - ================================================================================
2025-10-19 16:30:45 - INFO - 📦 Processing batch of 100 events...
2025-10-19 16:30:45 - INFO -   📊 ORDER_CREATED: 72 events
2025-10-19 16:30:45 - INFO -   📊 INVENTORY_ADJUSTED: 28 events
2025-10-19 16:30:45 - INFO -   ✅ Loaded 100 rows into staging table
2025-10-19 16:30:46 - INFO -   ⚡ Snowflake insert completed in 0.87s
2025-10-19 16:30:46 - INFO -   🎯 Total batch processing time: 1.23s
2025-10-19 16:30:46 - INFO - ✅ Batch committed successfully!
2025-10-19 16:30:46 - INFO - 📈 Session stats - Orders: 1247, Inventory: 453, Other: 0, Errors: 2
2025-10-19 16:30:46 - INFO - ================================================================================
```

### Errors
```
2025-10-19 16:31:12 - WARNING - ⚠️  Missing required field 'product_id' in ORDER_CREATED event
2025-10-19 16:31:12 - ERROR - ❌ JSON decode error at offset 12345: Expecting value: line 1 column 1 (char 0)
```

---

## 🎯 Event Validation

The consumer validates events based on their type:

### ORDER_CREATED
Required fields:
- `order_line_id`
- `customer_id`
- `product_id`
- `quantity`

### INVENTORY_ADJUSTED
Required fields:
- `event_id`
- `product_id`
- `quantity_change`
- `adjustment_type`

Invalid events are sent to the DLQ topic: `sales_events_dlq`

---

## 🔧 Configuration

### Batch Processing
```python
BATCH_SIZE = 100                    # Events per batch
COMMIT_INTERVAL_SECONDS = 10        # Max time before forced commit
```

### Kafka Consumer
```python
group_id = 'snowflake-ingestion-les-caves-albert-v1'
auto_offset_reset = 'earliest'
enable_auto_commit = False          # Manual commit for exactly-once semantics
```

---

## 📦 Dependencies

```bash
kafka-python==2.0.2
sqlalchemy==1.4.46
snowflake-sqlalchemy==1.4.7
pandas==2.0.0
prometheus-client==0.17.1
python-dotenv==1.0.0
```

---

## 🚨 Troubleshooting

### Staging Table Not Empty
```sql
-- Check staging table
SELECT COUNT(*) FROM stg_raw_events_stream;

-- Manual cleanup if needed
TRUNCATE TABLE stg_raw_events_stream;
```

### Metrics Not Showing in Grafana
1. Check Prometheus is scraping: http://localhost:9090/targets
2. Verify consumer is exposing metrics: http://localhost:8000/metrics
3. Check Prometheus datasource in Grafana

### High DLQ Rate
```bash
# Check DLQ topic for error details
kafka-console-consumer --bootstrap-server localhost:9092 \
  --topic sales_events_dlq \
  --from-beginning
```

---

## 📈 Performance Benchmarks

Expected performance (single consumer):
- **Throughput**: 300-500 events/second
- **Batch Processing**: < 2 seconds (p95)
- **Snowflake Insert**: < 1 second (p95)
- **Memory Usage**: ~200-300 MB

---

## 🔄 Graceful Shutdown

The consumer handles `SIGINT` (Ctrl+C) and `SIGTERM` gracefully:
1. Stops consuming new messages
2. Finishes processing current batch
3. Commits offsets to Kafka
4. Closes all connections
5. Logs final statistics

---

🍷 **Les Caves d'Albert** - Kafka Consumer v2.0 - October 2025
