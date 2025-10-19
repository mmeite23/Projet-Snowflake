# 🚀 Quick Start Guide - Les Caves d'Albert Consumer

## 📦 Installation

```bash
# Install Python dependencies
pip install kafka-python sqlalchemy snowflake-sqlalchemy pandas prometheus-client python-dotenv

# Or use requirements.txt
pip install -r requirements.txt
```

---

## 🔧 Configuration

### 1. Create `.env` file
```bash
cat > .env << 'EOF'
# Kafka Configuration
KAFKA_TOPIC_NAME=sales_events
KAFKA_BOOTSTRAP_SERVER=redpanda:9092

# Snowflake Configuration
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=SALES_DB
SNOWFLAKE_SCHEMA=RAW_DATA

# Metrics Configuration
METRICS_PORT=8000
EOF
```

---

## 🐳 Start Monitoring Stack

```bash
# Start Prometheus + Grafana
docker compose -f docker-compose-monitoring.yml up -d

# Check containers
docker compose -f docker-compose-monitoring.yml ps

# View logs
docker compose -f docker-compose-monitoring.yml logs -f
```

### Access Monitoring
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
  - Username: `admin`
  - Password: `admin123`

---

## ▶️ Run Consumer

```bash
# Basic run
python kafka_consumer_snowflake.py

# Run in background with logs
nohup python kafka_consumer_snowflake.py > consumer.log 2>&1 &

# Run with specific Python environment
/path/to/venv/bin/python kafka_consumer_snowflake.py
```

---

## 📊 Monitoring

### Check Metrics Endpoint
```bash
# View raw Prometheus metrics
curl http://localhost:8000/metrics

# Filter specific metrics
curl http://localhost:8000/metrics | grep kafka_events_consumed_total
curl http://localhost:8000/metrics | grep batch_processing_duration
```

### Prometheus Queries
```bash
# Open Prometheus UI
open http://localhost:9090

# Sample queries to run:
# 1. Events consumed per second
rate(kafka_events_consumed_total{status="success"}[1m])

# 2. Average batch processing time
rate(batch_processing_duration_seconds_sum[5m]) / rate(batch_processing_duration_seconds_count[5m])

# 3. Error rate
rate(dlq_messages_total[5m])
```

### Grafana Dashboard
```bash
# Open Grafana
open http://localhost:3000

# Navigate to:
# Dashboards → Les Caves d'Albert - Kafka Consumer Metrics
```

---

## 🗄️ Snowflake Queries

### Check Ingested Data
```sql
-- Connect to Snowflake
snowsql -a your_account -u your_user

-- Use database
USE DATABASE SALES_DB;
USE SCHEMA RAW_DATA;

-- Count total events
SELECT COUNT(*) as total_events FROM RAW_EVENTS_STREAM;

-- Count by event type
SELECT 
    EVENT_TYPE, 
    COUNT(*) as count 
FROM RAW_EVENTS_STREAM 
GROUP BY EVENT_TYPE;

-- Recent events
SELECT 
    EVENT_TYPE,
    PRODUCT_ID,
    CUSTOMER_ID,
    INGESTION_TIME
FROM RAW_EVENTS_STREAM
ORDER BY INGESTION_TIME DESC
LIMIT 10;

-- Staging table (should be empty)
SELECT COUNT(*) FROM stg_raw_events_stream;
```

### Sample Analytics Queries
```sql
-- Top 10 products ordered
SELECT 
    PRODUCT_ID,
    EVENT_CONTENT:product_name::VARCHAR as product_name,
    COUNT(*) as order_count
FROM RAW_EVENTS_STREAM
WHERE EVENT_TYPE = 'ORDER_CREATED'
GROUP BY PRODUCT_ID, product_name
ORDER BY order_count DESC
LIMIT 10;

-- Sales by channel
SELECT 
    EVENT_CONTENT:sales_channel::VARCHAR as channel,
    COUNT(*) as orders,
    SUM(EVENT_CONTENT:total_price::FLOAT) as total_revenue
FROM RAW_EVENTS_STREAM
WHERE EVENT_TYPE = 'ORDER_CREATED'
GROUP BY channel;

-- Inventory adjustments by type
SELECT 
    EVENT_CONTENT:adjustment_type::VARCHAR as adjustment_type,
    COUNT(*) as count,
    SUM(EVENT_CONTENT:quantity_change::INTEGER) as total_quantity_change
FROM RAW_EVENTS_STREAM
WHERE EVENT_TYPE = 'INVENTORY_ADJUSTED'
GROUP BY adjustment_type;
```

---

## 🔍 Debugging

### Check Consumer Logs
```bash
# View real-time logs
tail -f consumer.log

# Search for errors
grep "ERROR" consumer.log
grep "❌" consumer.log

# View batch statistics
grep "📈 Session stats" consumer.log
```

### Check Kafka Consumer Group
```bash
# View consumer group status
kafka-consumer-groups --bootstrap-server redpanda:9092 \
  --group snowflake-ingestion-les-caves-albert-v1 \
  --describe

# Reset consumer group (CAREFUL - reprocesses all messages)
kafka-consumer-groups --bootstrap-server redpanda:9092 \
  --group snowflake-ingestion-les-caves-albert-v1 \
  --reset-offsets --to-earliest --execute --topic sales_events
```

### Check DLQ Messages
```bash
# View messages in Dead Letter Queue
kafka-console-consumer --bootstrap-server redpanda:9092 \
  --topic sales_events_dlq \
  --from-beginning \
  --formatter kafka.tools.DefaultMessageFormatter \
  --property print.key=true \
  --property print.value=true
```

---

## 🛑 Stop Services

### Stop Consumer
```bash
# If running in foreground: Ctrl+C

# If running in background
pkill -f kafka_consumer_snowflake.py

# Or find and kill by PID
ps aux | grep kafka_consumer_snowflake.py
kill <PID>
```

### Stop Monitoring Stack
```bash
# Stop containers
docker compose -f docker-compose-monitoring.yml down

# Stop and remove volumes (data loss!)
docker compose -f docker-compose-monitoring.yml down -v
```

---

## 🔄 Common Operations

### Restart Consumer
```bash
# Stop consumer
pkill -f kafka_consumer_snowflake.py

# Clear logs
> consumer.log

# Restart
nohup python kafka_consumer_snowflake.py > consumer.log 2>&1 &

# Tail logs
tail -f consumer.log
```

### Reset Snowflake Tables
```sql
-- CAREFUL: This deletes all data!
TRUNCATE TABLE RAW_EVENTS_STREAM;
TRUNCATE TABLE stg_raw_events_stream;
```

### View Prometheus Targets
```bash
# Check if consumer is being scraped
open http://localhost:9090/targets

# Should show:
# kafka-consumer-snowflake (host.docker.internal:8000) - UP
```

---

## 📈 Performance Tuning

### Increase Batch Size
Edit `kafka_consumer_snowflake.py`:
```python
BATCH_SIZE = 200  # Default: 100
```

### Adjust Commit Interval
```python
COMMIT_INTERVAL_SECONDS = 5  # Default: 10
```

### Monitor Resource Usage
```bash
# CPU and Memory
top -p $(pgrep -f kafka_consumer_snowflake.py)

# Detailed stats
htop -p $(pgrep -f kafka_consumer_snowflake.py)
```

---

## 🧪 Testing

### Send Test Events
```bash
# Use the producer
python kafka_producer.py

# Send manual test event
kafka-console-producer --bootstrap-server redpanda:9092 \
  --topic sales_events << 'EOF'
{
  "event_type": "ORDER_CREATED",
  "order_line_id": "test-001",
  "customer_id": 1,
  "product_id": 1000,
  "product_name": "Test Wine",
  "quantity": 1,
  "unit_price": 10.0,
  "total_price": 10.0,
  "sales_channel": "E-com",
  "event_ts": "2025-10-19T12:00:00Z"
}
EOF
```

### Verify in Snowflake
```sql
SELECT * FROM RAW_EVENTS_STREAM
WHERE EVENT_CONTENT:order_line_id = 'test-001';
```

---

## 📚 Useful Links

- Prometheus UI: http://localhost:9090
- Grafana: http://localhost:3000
- Metrics Endpoint: http://localhost:8000/metrics
- Documentation: [KAFKA_CONSUMER_README.md](KAFKA_CONSUMER_README.md)

---

## 🆘 Troubleshooting Guide

| Issue | Solution |
|-------|----------|
| Consumer not connecting to Kafka | Check `KAFKA_BOOTSTRAP_SERVER` in `.env` |
| No data in Snowflake | Verify Snowflake credentials and permissions |
| Metrics not in Grafana | Check Prometheus is scraping at http://localhost:9090/targets |
| High DLQ rate | Check event schema validation and JSON format |
| Staging table not empty | Run `TRUNCATE TABLE stg_raw_events_stream;` |
| Out of memory | Reduce `BATCH_SIZE` |

---

🍷 **Les Caves d'Albert** - Quick Start Guide - October 2025
