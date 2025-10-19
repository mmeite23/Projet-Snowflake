# 🏗️ Repository Organization

This document explains the new, professional structure of the **Les Caves d'Albert** repository.

## ✨ New Structure (October 2025)

The repository has been reorganized for better clarity, maintainability, and professional standards.

### 📂 Directory Layout

```
Projet-Snowflake/
├── 📊 sql/                    SQL Scripts
├── 📈 streamlit/              Streamlit BI Dashboard
├── 📉 monitoring/             Prometheus + Grafana
├── 🐳 docker/                 Docker configuration
├── 📓 notebooks/              Jupyter notebooks
├── 🚀 streaming/              Kafka producer/consumer
├── 📦 batch-ingestion/        Historical data loading
├── 📚 documentation/          Comprehensive docs (13 files)
└── 📊 data/                   Test data
```

---

## 🎯 What Changed

### Before (Cluttered Root)
```
/
├── snowflake-tasks-streams.sql          ❌ SQL at root
├── analytical-queries.sql                ❌ SQL at root
├── streamlit_dashboard_snowflake.py      ❌ Streamlit at root
├── docker-compose.yml                    ❌ Docker at root
├── docker-compose-monitoring.yml         ❌ Docker at root
├── Dockerfile                            ❌ Docker at root
├── prometheus.yml                        ❌ Monitoring at root
├── grafana-dashboard-consumer.json       ❌ Monitoring at root
├── Git_Basics.ipynb                      ❌ Notebook at root
└── 20+ files at root level               ❌ Hard to navigate
```

### After (Organized)
```
/
├── sql/
│   └── snowflake/
│       ├── snowflake-tasks-streams.sql   ✅ Organized by purpose
│       └── analytical-queries.sql         ✅ Clear location
│
├── streamlit/
│   └── dashboard.py                       ✅ Renamed & organized
│
├── docker/
│   ├── docker-compose.yml                 ✅ All Docker together
│   ├── docker-compose-monitoring.yml      ✅ Clear separation
│   └── Dockerfile                         ✅ Easy to find
│
├── monitoring/
│   ├── prometheus.yml                     ✅ Monitoring centralized
│   ├── grafana-provisioning/              ✅ Auto-provisioning
│   └── grafana/dashboards/                ✅ Dashboard exports
│
└── notebooks/
    └── Git_Basics.ipynb                   ✅ Educational materials
```

---

## 📊 Directory Purposes

### `sql/` - SQL Scripts
**Purpose**: All SQL code for Snowflake
- `snowflake/snowflake-tasks-streams.sql` - Main ELT automation pipeline
- `snowflake/analytical-queries.sql` - 50+ business intelligence queries

**Usage**:
```bash
# Execute in Snowflake UI
USE DATABASE CAVES_ALBERT_DB;
@sql/snowflake/snowflake-tasks-streams.sql
```

---

### `streamlit/` - Business Intelligence Dashboard
**Purpose**: Real-time analytics dashboard running in Snowflake
- `dashboard.py` - Main Streamlit application (formerly `streamlit_dashboard_snowflake.py`)

**Features**:
- 5 KPIs (Orders, Customers, Revenue, Avg Basket, Items Sold)
- Interactive charts and filters
- Inventory management and alerts

**Deployment**:
- Snowflake UI → Streamlit → Create App → Copy code from `dashboard.py`

---

### `monitoring/` - Monitoring Stack
**Purpose**: Prometheus + Grafana for pipeline observability
- `prometheus.yml` - Metrics collection configuration
- `grafana-provisioning/` - Auto-provisioning for dashboards and datasources
- `grafana/dashboards/` - Exported dashboard JSON files

**Access**:
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

**Metrics**: 11 Prometheus metrics tracking consumer health

---

### `docker/` - Container Orchestration
**Purpose**: Docker Compose and Dockerfile for infrastructure
- `docker-compose.yml` - Main stack (Kafka + Consumer)
- `docker-compose-monitoring.yml` - Monitoring stack
- `Dockerfile` - Consumer container image

**Usage**:
```bash
# Start main stack
docker compose -f docker/docker-compose.yml up -d

# Start monitoring
docker compose -f docker/docker-compose-monitoring.yml up -d
```

---

### `notebooks/` - Jupyter Notebooks
**Purpose**: Educational and exploratory analysis
- `Git_Basics.ipynb` - Git fundamentals tutorial

**Usage**:
```bash
jupyter notebook notebooks/Git_Basics.ipynb
```

---

### `streaming/` - Real-Time Streaming (Unchanged)
**Purpose**: Kafka producer and consumer
- `kafka_producer.py` - Generates wine sales events
- `kafka_consumer_snowflake.py` - Ingests to Snowflake with monitoring

---

### `batch-ingestion/` - Historical Data (Unchanged)
**Purpose**: SQLite-based batch data loading
- Jupyter notebooks for generating historical sales data

---

### `documentation/` - Comprehensive Documentation (Unchanged)
**Purpose**: 13 detailed markdown files
- Architecture diagrams
- Deployment guides
- API references
- Troubleshooting

---

## 🎯 Benefits of New Structure

### ✅ Developer Experience
- **Faster navigation** - Find files by category
- **Clear intent** - Directory names explain purpose
- **Better IDE support** - Logical folder grouping

### ✅ Maintainability
- **Easier updates** - Related files together
- **Reduced cognitive load** - Less clutter at root
- **Scalability** - Easy to add new components

### ✅ Professional Standards
- **Industry best practices** - Standard project layout
- **Better for teams** - Clear onboarding path
- **CI/CD friendly** - Organized for automation

---

## 🔄 Migration Guide

If you have local checkouts or scripts referencing old paths:

### Update Docker Commands
**Before:**
```bash
docker compose -f docker-compose.yml up
```

**After:**
```bash
docker compose -f docker/docker-compose.yml up
```

### Update SQL Paths
**Before:**
```bash
snowsql -f snowflake-tasks-streams.sql
```

**After:**
```bash
snowsql -f sql/snowflake/snowflake-tasks-streams.sql
```

### Update Streamlit References
**Before:**
- File: `streamlit_dashboard_snowflake.py`

**After:**
- File: `streamlit/dashboard.py`

---

## 📝 Documentation Updates

Each new directory has a `README.md` with:
- ✅ Purpose and overview
- ✅ File descriptions
- ✅ Usage examples
- ✅ Configuration guides
- ✅ Links to related docs

**Read these READMEs:**
- [sql/README.md](sql/README.md)
- [streamlit/README.md](streamlit/README.md)
- [monitoring/README.md](monitoring/README.md)
- [docker/README.md](docker/README.md)
- [notebooks/README.md](notebooks/README.md)

---

## 🚀 Quick Start with New Structure

```bash
# 1. Clone repository
git clone https://github.com/mmeite23/Projet-Snowflake.git
cd Projet-Snowflake

# 2. Start Docker services
docker compose -f docker/docker-compose.yml up -d
docker compose -f docker/docker-compose-monitoring.yml up -d

# 3. Execute Snowflake automation
# (In Snowflake UI)
@sql/snowflake/snowflake-tasks-streams.sql

# 4. Deploy Streamlit dashboard
# (Copy code from streamlit/dashboard.py to Snowflake Streamlit)

# 5. Access monitoring
open http://localhost:3000  # Grafana
open http://localhost:9090  # Prometheus
```

---

## 📞 Questions?

If you have questions about the new structure:
1. Check the README.md in each directory
2. See [documentation/README.md](documentation/README.md) for comprehensive docs
3. Open an issue on GitHub

---

**🍷 Les Caves d'Albert** - October 2025 Reorganization
