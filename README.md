# 🍷 Les Caves d'Albert - Wine Sales Event Streaming System

[![Kafka](https://img.shields.io/badge/Kafka-Stream-black?logo=apache-kafka)](https://kafka.apache.org/)
[![Snowflake](https://img.shields.io/badge/Snowflake-Data_Warehouse-blue?logo=snowflake)](https://www.snowflake.com/)
[![Prometheus](https://img.shields.io/badge/Prometheus-Monitoring-orange?logo=prometheus)](https://prometheus.io/)
[![Grafana](https://img.shields.io/badge/Grafana-Visualization-yellow?logo=grafana)](https://grafana.com/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-blue?logo=docker)](https://www.docker.com/)

Production-ready event streaming pipeline for wine sales data, with real-time ingestion to Snowflake and comprehensive Prometheus/Grafana monitoring.

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Monitoring](#-monitoring)
- [Documentation](#-documentation)
- [Project Structure](#-project-structure)

---

## 🎯 Overview

**Les Caves d'Albert** is a real-time data streaming system designed for wine sales analytics. The system:

- **Generates** realistic wine sales events (orders, inventory adjustments) with French wine data 🍷
- **Streams** events through Kafka (RedPanda) for reliable, scalable message processing
- **Ingests** data into Snowflake using ELT architecture for analytics-ready storage
- **Monitors** the entire pipeline with 11 Prometheus metrics and 8 Grafana dashboard panels

### Event Types

1. **ORDER_CREATED** (70%): Customer purchases with complete product details
   - Product names, categories (Rouge 🍷, Blanc 🥂, Rosé 🌸, Effervescent 🍾, Spiritueux 🥃)
   - Pricing with occasional discounts (25% chance)
   - Sales channels (E-com, Boutique Paris, Lyon, Bordeaux)

2. **INVENTORY_ADJUSTED** (30%): Stock movements with warehouse tracking
   - Adjustment types: REPLENISHMENT, CORRECTION, SPOILAGE
   - Warehouse locations and batch details

---

## 🏗️ Architecture

```
┌──────────────────┐
│  Kafka Producer  │  🛒 Generates wine sales events with emojis & details
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   RedPanda       │  📨 Kafka-compatible message broker (sales_events topic)
│  (Kafka broker)  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Kafka Consumer  │  📦 Ingests to Snowflake RAW_EVENTS_STREAM table
│   + Prometheus   │  📊 Exports 11 metrics on port 8000
└────────┬─────────┘
         │
         ├─────────────────────┐
         ▼                     ▼
┌──────────────────┐   ┌──────────────────┐
│   Snowflake      │   │   Prometheus     │  📈 Scrapes metrics every 15s
│  Data Warehouse  │   │   + Grafana      │  📊 8-panel dashboard
└──────────────────┘   └──────────────────┘
```

### Data Flow

1. **Producer** generates events → `sales_events` topic
2. **RedPanda** buffers messages for reliable delivery
3. **Consumer** reads batches → validates schema → inserts to Snowflake
4. **Snowflake** stores events in `RAW_EVENTS_STREAM` table (EVENT_TYPE, PRODUCT_ID, CUSTOMER_ID indexed)
5. **Prometheus** scrapes consumer metrics every 15 seconds
6. **Grafana** visualizes metrics in real-time dashboard

---

## ✨ Features

### Producer (`kafka_producer.py`)
- 🍷 **Realistic wine data** with French product names (Merlot, Chardonnay, etc.)
- 🎨 **Category emojis** for visual identification (🍷 Rouge, 🥂 Blanc, 🌸 Rosé, 🍾 Effervescent, 🥃 Spiritueux)
- 💰 **Pricing logic** with discounts (25% chance on orders)
- 📦 **Warehouse tracking** for inventory adjustments
- 🔄 **Consistent data generation** using product_id-based seeding
- 📝 **English logs with emojis** for international collaboration

### Consumer (`kafka_consumer_snowflake.py`)
- ✅ **Schema validation** per event type (required fields checked)
- 📊 **11 Prometheus metrics**: Counters, Histograms, Gauges, Summary
- 🗄️ **Enhanced Snowflake schema** with indexed columns (EVENT_TYPE, PRODUCT_ID, CUSTOMER_ID)
- 🚨 **Dead Letter Queue (DLQ)** for invalid events
- 🧹 **Staging table monitoring** ensures stg_raw_events_stream stays empty
- 🔁 **Batch processing** with configurable size (default: 100 events)
- 📈 **Session statistics** logged every batch (running totals)
- 🛑 **Graceful shutdown** on SIGINT/SIGTERM

### Monitoring Stack
- 📈 **Prometheus** metrics collection (port 9090)
- 📊 **Grafana** dashboard with 8 panels (port 3000, login: admin/admin123)
- 🔄 **Auto-provisioning** for datasources and dashboards
- 📦 **Persistent volumes** for metrics history
- 🎯 **Real-time visibility** into events consumed, batch sizes, processing duration, DLQ messages

---

## 📦 Prerequisites

1. **Docker & Docker Compose** (for containerized deployment)
2. **Snowflake Account** with:
   - Warehouse (e.g., `COMPUTE_WH`)
   - Database (e.g., `WINE_SALES_DB`)
   - Schema (e.g., `RAW_DATA`)
   - User with CREATE TABLE privileges
3. **Environment Variables** (see Configuration section)

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/mmeite23/Projet-Snowflake.git
cd Projet-Snowflake
```

### 2. Configure Environment Variables

Create a `.env` file with your Snowflake credentials:

```bash
# Kafka Configuration
KAFKA_TOPIC_NAME=sales_events

# Snowflake Credentials (⚠️ NEVER COMMIT THIS FILE)
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account.region
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=WINE_SALES_DB
SNOWFLAKE_SCHEMA=RAW_DATA
```

**⚠️ SECURITY**: The `.env` file is already in `.gitignore` to prevent credential leaks.

### 3. Start the Main Stack (Kafka + Producer + Consumer)

```bash
docker-compose up -d
```

This starts:
- **RedPanda** (Kafka broker) on port 19092
- **RedPanda Console** (UI) on port 8080
- **Producer** generating events
- **Consumer** ingesting to Snowflake + exporting metrics on port 8000

### 4. Start the Monitoring Stack (Prometheus + Grafana)

```bash
docker-compose -f docker-compose-monitoring.yml up -d
```

This starts:
- **Prometheus** on [http://localhost:9090](http://localhost:9090)
- **Grafana** on [http://localhost:3000](http://localhost:3000) (login: `admin` / `admin123`)

### 5. Verify Everything is Running

```bash
# Check all containers
docker ps

# View producer logs
docker logs producer -f

# View consumer logs
docker logs consumer -f

# Check Kafka topics
docker exec -it redpanda rpk topic list
```

### 6. Access Monitoring Dashboards

- **Grafana Dashboard**: [http://localhost:3000/d/kafka-consumer-snowflake](http://localhost:3000/d/kafka-consumer-snowflake)
  - Events consumed rate
  - Total events counter
  - Batch size distribution
  - Processing duration percentiles (p50, p95)
  - Snowflake insert performance
  - DLQ error messages
  - Real-time event summary table

- **Prometheus Metrics**: [http://localhost:8000/metrics](http://localhost:8000/metrics)
  - Raw metrics endpoint from consumer

- **RedPanda Console**: [http://localhost:8080](http://localhost:8080)
  - Kafka topic inspection and message browser

---

## ⚙️ Configuration

### Producer Settings

Edit `kafka_producer.py` to adjust:
- `EVENT_GENERATION_DELAY = 1`: Seconds between events
- `ORDER_CREATED_PROBABILITY = 0.7`: 70% orders, 30% inventory adjustments
- `PRODUCT_ID_RANGE = (1000, 1049)`: Product ID range (50 products)
- `CUSTOMER_ID_RANGE = (1, 150)`: Customer ID range (150 customers)

### Consumer Settings

Edit `kafka_consumer_snowflake.py` to adjust:
- `BATCH_SIZE = 100`: Number of events per Snowflake batch
- `CONSUMER_TIMEOUT_MS = 1000`: Kafka consumer poll timeout
- `GROUP_ID = "snowflake-ingestion-group"`: Kafka consumer group

### Snowflake Schema

The consumer automatically creates the `RAW_EVENTS_STREAM` table:

```sql
CREATE TABLE IF NOT EXISTS RAW_EVENTS_STREAM (
    EVENT_TYPE VARCHAR(50),        -- Indexed for filtering
    PRODUCT_ID INTEGER,             -- Indexed for product analytics
    CUSTOMER_ID INTEGER,            -- Indexed for customer analytics
    EVENT_METADATA OBJECT,          -- Full JSON metadata
    EVENT_CONTENT VARIANT,          -- Full event JSON
    INGESTION_TIME TIMESTAMP_LTZ    -- Automatic timestamp
);
```

---

## 📊 Monitoring

### Prometheus Metrics (11 total)

**Counters** (ever-increasing):
- `kafka_events_consumed_total`: Total events read from Kafka
- `kafka_events_inserted_snowflake_total`: Total events inserted to Snowflake
- `kafka_events_dlq_total`: Total invalid events sent to DLQ

**Histograms** (distribution + percentiles):
- `kafka_batch_size`: Batch size distribution (p50, p90, p95, p99)
- `kafka_batch_processing_duration_seconds`: Batch processing time
- `snowflake_insert_duration_seconds`: Snowflake insert time

**Gauges** (current value):
- `kafka_current_batch_size`: Current batch size
- `kafka_snowflake_insert_rows`: Last insert row count
- `kafka_consumer_lag`: Consumer lag (if available)

**Summary** (sliding window statistics):
- `kafka_event_size_bytes`: Event payload size distribution

### Grafana Dashboard Panels (8 total)

1. **Events Consumed Rate** (events/sec over time)
2. **Total Events Consumed** (cumulative counter)
3. **Current Batch Size** (real-time gauge)
4. **Batch Processing Duration** (p50, p95 percentiles)
5. **Snowflake Insert Duration** (p50, p95 percentiles)
6. **Events Inserted to Snowflake** (rate over time)
7. **DLQ Messages** (error counter)
8. **Events Summary** (table with event types and totals)

---

## 📚 Documentation

- **[KAFKA_PRODUCER_IMPROVEMENTS.md](KAFKA_PRODUCER_IMPROVEMENTS.md)**: Producer enhancements with emojis and product details
- **[KAFKA_CONSUMER_README.md](KAFKA_CONSUMER_README.md)**: Complete technical documentation (3500 words) with architecture, metrics reference, troubleshooting
- **[QUICK_START.md](QUICK_START.md)**: Operational guide (1500 words) with setup commands, monitoring queries, debugging tips
- **[CONSUMER_IMPROVEMENTS.md](CONSUMER_IMPROVEMENTS.md)**: Summary of all improvements with before/after comparisons
- **[SAMPLE_OUTPUT.md](SAMPLE_OUTPUT.md)**: Example logs and JSON events from producer/consumer
- **[GITHUB_PUSH_AUDIT.md](GITHUB_PUSH_AUDIT.md)**: File audit for repository cleanup

---

## 📁 Project Structure

```
Projet-Snowflake/
├── README.md                                 # 👈 You are here
├── .env                                      # 🔒 Credentials (ignored)
├── .gitignore                                # 🚫 Git ignore rules
│
├── batch-ingestion/                          # 📦 BATCH INGESTION
│   ├── README.md                             # Batch documentation
│   ├── Data_generator_faker.ipynb            # Fake data generator (SQLite)
│   ├── Pipeline.ipynb                        # SQLite → Snowflake pipeline
│   ├── Git_Basics.ipynb                      # Git tutorial
│   └── Screenshot Snwoflake.png              # Historical screenshot
│
├── streaming/                                # � REAL-TIME STREAMING
│   ├── README.md                             # Streaming documentation
│   ├── kafka_producer.py                     # Event generator
│   ├── kafka_consumer_snowflake.py           # Snowflake ingestion
│   └── requirements-consumer.txt             # Python dependencies
│
├── Dockerfile                                # 🐳 Container build (streaming)
├── docker-compose.yml                        # 🐳 Main stack (Kafka + streaming)
├── docker-compose-monitoring.yml             # 🐳 Monitoring stack
├── prometheus.yml                            # 📈 Prometheus config
├── grafana-dashboard-consumer.json           # 📊 Grafana dashboard
│
├── grafana-provisioning/                     # 🔧 Auto-provisioning
│   ├── datasources/
│   │   └── prometheus.yml
│   └── dashboards/
│       └── dashboard.yml
│
├── KAFKA_PRODUCER_IMPROVEMENTS.md            # 📝 Documentation
├── KAFKA_CONSUMER_README.md                  # 📝 Documentation
├── QUICK_START.md                            # 📝 Documentation
├── CONSUMER_IMPROVEMENTS.md                  # 📝 Documentation
├── SAMPLE_OUTPUT.md                          # 📝 Documentation
└── GITHUB_PUSH_AUDIT.md                      # 📝 Audit report
```

### Directory Organization

**`batch-ingestion/`** - Historical data loading
- Jupyter notebooks for generating and loading batch data
- SQLite-based approach for initial data seeding
- Ideal for loading historical sales data (1 year+)
- See [batch-ingestion/README.md](batch-ingestion/README.md) for details

**`streaming/`** - Real-time event streaming
- Kafka producer and consumer for live event processing
- Prometheus metrics and production-ready features
- Ideal for real-time sales analytics and monitoring
- See [streaming/README.md](streaming/README.md) for details

---

## 🛠️ Development

### Running Locally (without Docker)

1. **Install Python dependencies**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements-consumer.txt
   ```

2. **Start RedPanda locally** (or use existing Kafka):
   ```bash
   docker run -d --name redpanda \
     -p 19092:19092 -p 9644:9644 \
     docker.redpanda.com/redpandadata/redpanda:latest \
     redpanda start --smp 1 --overprovisioned --node-id 0 \
     --kafka-addr INTERNAL://0.0.0.0:9092,OUTSIDE://0.0.0.0:19092 \
     --advertise-kafka-addr INTERNAL://redpanda:9092,OUTSIDE://localhost:19092
   ```

3. **Run producer**:
   ```bash
   python kafka_producer.py
   ```

4. **Run consumer**:
   ```bash
   python kafka_consumer_snowflake.py
   ```

### Troubleshooting

**Problem**: Consumer can't connect to Snowflake
- ✅ Check `.env` file has correct credentials
- ✅ Verify Snowflake account is active
- ✅ Ensure warehouse is running (auto-suspend disabled recommended)

**Problem**: No events appearing in Grafana
- ✅ Check consumer is running: `docker logs consumer -f`
- ✅ Verify Prometheus is scraping: [http://localhost:9090/targets](http://localhost:9090/targets)
- ✅ Ensure metrics port 8000 is exposed: `curl http://localhost:8000/metrics`

**Problem**: Staging table has data (`stg_raw_events_stream`)
- ✅ Consumer checks at startup and logs warning if not empty
- ✅ This is a temporary table for pandas→Snowflake bridge, should auto-clean
- ✅ If persists, manually truncate: `TRUNCATE TABLE stg_raw_events_stream;`

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open-source and available for educational and commercial use.

---

## � Authors

- **Mory Meite** - [@mmeite23](https://github.com/mmeite23)
- **Dalanda Diallo**
- **Roger Daoud**
- **Mario Daoud**
- **Maxandre Michel**

Project: [Projet-Snowflake](https://github.com/mmeite23/Projet-Snowflake)

---

## 🎉 Acknowledgments

- **RedPanda** for Kafka-compatible streaming
- **Snowflake** for cloud data warehouse
- **Prometheus** for metrics collection
- **Grafana** for beautiful dashboards
- **Les Caves d'Albert** for the wine business context 🍷

---

**Ready to stream wine sales! 🚀🍷**
