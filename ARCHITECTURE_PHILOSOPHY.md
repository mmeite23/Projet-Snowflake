# 🍷 Projet Snowflake - Architecture & Philosophy

## 🎯 Overview

**Les Caves d'Albert** is a comprehensive wine sales data ingestion system to Snowflake, supporting **two complementary approaches**:

1. **Batch Ingestion** 📦 - For loading historical data (years of data)
2. **Streaming** 🚀 - For capturing real-time sales

---

## 📂 Project Organization

```
Projet-Snowflake/
│
├── 📦 batch-ingestion/          Batch ingestion (historical)
│   ├── Data_generator_faker.ipynb    Fake data generator
│   ├── Pipeline.ipynb                SQLite → Snowflake pipeline
│   ├── Git_Basics.ipynb              Git tutorial (reference)
│   └── README.md                     Batch documentation
│
├── 🚀 streaming/                Real-time ingestion
│   ├── kafka_producer.py             Event generator
│   ├── kafka_consumer_snowflake.py   Kafka → Snowflake ingestion
│   ├── requirements-consumer.txt     Python dependencies
│   └── README.md                     Streaming documentation
│
├── 🐳 Docker & Orchestration
│   ├── Dockerfile                    Build producer/consumer
│   ├── docker-compose.yml            Main stack (Kafka)
│   └── docker-compose-monitoring.yml Prometheus + Grafana
│
├── 📊 Monitoring
│   ├── prometheus.yml                Prometheus config
│   ├── grafana-dashboard-consumer.json Grafana dashboard
│   └── grafana-provisioning/         Auto-provisioning
│
└── 📝 Documentation
    ├── README.md                     Main documentation
    ├── KAFKA_PRODUCER_IMPROVEMENTS.md
    ├── KAFKA_CONSUMER_README.md
    ├── QUICK_START.md
    ├── CONSUMER_IMPROVEMENTS.md
    ├── SAMPLE_OUTPUT.md
    ├── GITHUB_PUSH_AUDIT.md
    └── REORGANIZATION_SUMMARY.md
```

---

## 🔄 Batch vs Streaming: When to Use What?

### 📦 Batch Ingestion (`batch-ingestion/`)

**When to use:**
- ✅ Initial historical data loading (1+ years)
- ✅ Migration from existing system
- ✅ Already consolidated data (end of day, end of month)
- ✅ No real-time requirement
- ✅ Large volumes to load at once

**Technologies:**
- SQLite for local data generation/storage
- Pandas for data manipulation
- Jupyter Notebooks for interactivity
- SQLAlchemy for Snowflake connection

**Workflow:**
```
1. Data_generator_faker.ipynb → Generates wine_data.db (SQLite)
2. Pipeline.ipynb → Reads SQLite and loads to Snowflake
3. Snowflake schema: BATCH_DATA (tables: customers, inventory, sales)
```

---

### 🚀 Streaming (`streaming/`)

**When to use:**
- ✅ Real-time events (sales, inventory)
- ✅ Low-latency analytics (< 1 second)
- ✅ Live monitoring (live dashboards)
- ✅ Data-driven alerts
- ✅ Event-driven architecture

**Technologies:**
- Kafka (RedPanda) for streaming
- Python Producer to generate events
- Python Consumer to ingest to Snowflake
- Prometheus for metrics collection
- Grafana for visualization

**Workflow:**
```
1. kafka_producer.py → Generates events → Kafka Topic
2. kafka_consumer_snowflake.py → Consumes → Snowflake RAW_EVENTS_STREAM
3. Prometheus scrapes metrics → Grafana visualizes
4. Snowflake schema: RAW_DATA (table: RAW_EVENTS_STREAM)
```

---

## 🎨 Hybrid Architecture (Recommended)

For a complete project, **combine both approaches**:

### Phase 1: Batch (Historical Data)
```bash
cd batch-ingestion
jupyter notebook Data_generator_faker.ipynb  # Generate data
jupyter notebook Pipeline.ipynb              # Load to Snowflake
```
➡️ Result: **1 year of historical data** in `BATCH_DATA` schema

### Phase 2: Streaming (Real-Time)
```bash
docker-compose up -d                          # Start Kafka + Producer + Consumer
docker-compose -f docker-compose-monitoring.yml up -d  # Monitoring
```
➡️ Result: **Live events** in `RAW_DATA` schema

### Phase 3: Consolidation in Snowflake
```sql
-- Unified batch + streaming view
CREATE VIEW consolidated_sales AS
SELECT 
    sale_date,
    customer_id,
    product_id,
    quantity_sold,
    total_price,
    'BATCH' as source
FROM BATCH_DATA.sales

UNION ALL

SELECT 
    PARSE_JSON(event_content):timestamp::TIMESTAMP as sale_date,
    PARSE_JSON(event_content):customer_id::INTEGER as customer_id,
    PARSE_JSON(event_content):product_id::INTEGER as product_id,
    PARSE_JSON(event_content):quantity::INTEGER as quantity_sold,
    PARSE_JSON(event_content):total_price::DECIMAL(10,2) as total_price,
    'STREAMING' as source
FROM RAW_DATA.raw_events_stream
WHERE event_type = 'ORDER_CREATED';

-- Now you have EVERYTHING: historical + real-time!
```

---

## 🌟 Project Strengths

### 1. **Clear Separation of Concerns**
- `batch-ingestion/` = Everything related to notebooks and SQLite
- `streaming/` = Everything related to Kafka and real-time
- Easy to navigate, understand, and maintain

### 2. **Comprehensive Documentation**
- README in each folder (`batch-ingestion/README.md`, `streaming/README.md`)
- Detailed technical documentation (KAFKA_CONSUMER_README.md: 3500 words)
- Operational guide (QUICK_START.md: 1500 words)
- Log and JSON examples (SAMPLE_OUTPUT.md)

### 3. **Production-Ready**
- ✅ Complete monitoring (11 Prometheus metrics)
- ✅ Grafana dashboard with 8 panels
- ✅ Schema validation per event type
- ✅ Dead Letter Queue for errors
- ✅ Graceful shutdown
- ✅ Professional English logs with emojis

### 4. **Realistic Data**
- French wine names (Merlot, Chardonnay, Syrah, etc.)
- Categories with emojis (🍷 Rouge, 🥂 Blanc, 🌸 Rosé, 🍾 Effervescent, 🥃 Spiritueux)
- Pricing logic with discounts
- Consistent generation via seeding

### 5. **Security**
- Credentials in `.env` (never committed)
- Complete `.gitignore` to prevent leaks
- Non-root user in Docker
- Multi-stage build for lean images

---

## 🎓 Learning Use Cases

This project is ideal for learning:

1. **Event Streaming with Kafka**
   - Producing and consuming messages
   - Topics, partitions, consumer groups
   - JSON serialization

2. **Data Warehousing with Snowflake**
   - ELT architecture (Event, Load, Transform)
   - Tables with VARIANT columns for JSON
   - Optimization with indexed columns

3. **Monitoring with Prometheus/Grafana**
   - Metrics (Counters, Histograms, Gauges)
   - Scraping and retention
   - Dashboards and alerting

4. **Docker & Orchestration**
   - Multi-container with docker-compose
   - Volumes for persistence
   - Networks for isolation

5. **Production Python Code**
   - Error handling with try/except
   - Structured logging
   - Graceful shutdown
   - Environment variables

---

## 🚀 Quick Start

### Batch Ingestion (5 minutes)
```bash
cd batch-ingestion
pip install faker pandas jupyter
jupyter notebook Data_generator_faker.ipynb  # Execute all cells
jupyter notebook Pipeline.ipynb              # Execute all cells
```

### Streaming (2 minutes)
```bash
cd /Users/mory_jr/Projet-Snowflake
docker-compose up -d
docker logs producer -f  # See events being generated
```

### Monitoring (1 minute)
```bash
docker-compose -f docker-compose-monitoring.yml up -d
open http://localhost:3000  # Grafana (admin/admin123)
```

---

## 📊 Success Metrics

After starting the system, you should see:

- ✅ **Producer**: 1 event/second in logs
- ✅ **Consumer**: Batches of 100 events ingested to Snowflake
- ✅ **Prometheus**: Target "consumer" in UP state
- ✅ **Grafana**: Dashboard with metrics climbing
- ✅ **Snowflake**: Table `RAW_EVENTS_STREAM` filling up

---

## 🤝 Contributing

This project is organized to facilitate contributions:

1. **Batch**: Improve notebooks in `batch-ingestion/`
2. **Streaming**: Improve producer/consumer in `streaming/`
3. **Monitoring**: Add Grafana panels in `grafana-dashboard-consumer.json`
4. **Documentation**: Complete READMEs in each folder

---

## 🎯 Future Roadmap

### Batch Ingestion
- [ ] CSV support in addition to SQLite
- [ ] Airflow pipeline for orchestration
- [ ] Data validation with Great Expectations

### Streaming
- [ ] Avro support for serialization
- [ ] Kafka Streams for transformations
- [ ] Schema Registry for schema evolution
- [ ] Consumer group with multiple instances
- [ ] Alerting with Alertmanager

### Snowflake
- [ ] dbt models for transformations
- [ ] Streams and Tasks for incremental processing
- [ ] Time Travel for auditing
- [ ] Dynamic Tables for aggregations

---

**This project demonstrates a complete data engineering architecture, from ingestion to visualization! 🍷📊**
