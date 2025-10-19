# 📚 Documentation - Les Caves d'Albert

This folder contains all technical documentation for the Snowflake project.

## 📖 Table of Contents

### 🚀 Getting Started Guides

| File | Description | Read if... |
|------|-------------|------------|
| **[QUICKSTART.md](./QUICKSTART.md)** | Quick start in 3 steps | You're starting the project |
| **[QUICK_START.md](./QUICK_START.md)** | Original startup guide | Historical reference |
| **[README-DEPLOYMENT.md](./README-DEPLOYMENT.md)** | Complete deployment guide (200+ lines) | You want all the details |

### 🏗️ Architecture

| File | Description | Content |
|------|-------------|---------|
| **[ARCHITECTURE_DIAGRAM.md](./ARCHITECTURE_DIAGRAM.md)** | Visual pipeline diagrams | RAW → STAGING → PRODUCTION schemas |
| **[ARCHITECTURE_PHILOSOPHY.md](./ARCHITECTURE_PHILOSOPHY.md)** | Design philosophy and principles | Understand technical choices |

### ⚙️ Snowflake Configuration

| File | Description | Use for... |
|------|-------------|------------|
| **[SNOWFLAKE_AUTOMATION_GUIDE.md](./SNOWFLAKE_AUTOMATION_GUIDE.md)** | Automation guide with Tasks & Streams | Understanding CDC and automation |
| **[SNOWFLAKE_TASKS_README.md](./SNOWFLAKE_TASKS_README.md)** | Snowflake Tasks documentation | Reference for created tasks |

### 🔧 Kafka & Streaming Configuration

| File | Description | Content |
|------|-------------|---------|
| **[KAFKA_PRODUCER_IMPROVEMENTS.md](./KAFKA_PRODUCER_IMPROVEMENTS.md)** | Kafka producer improvements | Optimizations and features |
| **[KAFKA_CONSUMER_README.md](./KAFKA_CONSUMER_README.md)** | Consumer documentation | Configuration and usage |
| **[CONSUMER_IMPROVEMENTS.md](./CONSUMER_IMPROVEMENTS.md)** | Consumer improvements | Enhancements and performance |

### 📊 Examples and Outputs

| File | Description | Content |
|------|-------------|---------|
| **[SAMPLE_OUTPUT.md](./SAMPLE_OUTPUT.md)** | Pipeline output examples | Expected logs and results |

---

## 🎯 Where to Start?

### **Level 1: Quick Start (5 minutes)**
1. Read [QUICKSTART.md](./QUICKSTART.md)
2. Execute the SQL script
3. Verify it works

### **Level 2: Deep Understanding (20 minutes)**
1. Read [README-DEPLOYMENT.md](./README-DEPLOYMENT.md)
2. Review [ARCHITECTURE_DIAGRAM.md](./ARCHITECTURE_DIAGRAM.md)
3. Explore [SNOWFLAKE_AUTOMATION_GUIDE.md](./SNOWFLAKE_AUTOMATION_GUIDE.md)

### **Level 3: Maintenance and Monitoring (30+ minutes)**
1. Study [SNOWFLAKE_TASKS_README.md](./SNOWFLAKE_TASKS_README.md)
2. Test monitoring queries
3. Customize the pipeline to your needs

---

## 📊 Project Structure

```
Projet-Snowflake/
├── documentation/              # 📚 This folder
│   ├── README.md              # Index (this file)
│   ├── QUICKSTART.md          # Quick guide
│   ├── README-DEPLOYMENT.md   # Complete guide
│   ├── ARCHITECTURE_DIAGRAM.md # Diagrams
│   ├── SNOWFLAKE_AUTOMATION_GUIDE.md
│   └── SNOWFLAKE_TASKS_README.md
│
├── streaming/                  # Python code
│   ├── kafka_producer.py      # Generates events
│   └── kafka_consumer_snowflake.py # Snowflake ingestion
│
├── *.sql                       # SQL scripts
│   ├── snowflake-tasks-streams-CORRECTED.sql ⭐
│   ├── analytical-queries.sql
│   ├── fix-*.sql
│   └── execute-tasks-now.sql
│
└── docker-compose.yml          # Infrastructure
```

---

## 🔗 Quick Links

### Main SQL Scripts
- 🎯 **[../snowflake-tasks-streams-CORRECTED.sql](../snowflake-tasks-streams-CORRECTED.sql)** - Main script to execute
- 📊 **[../analytical-queries.sql](../analytical-queries.sql)** - 50+ analytical queries
- 🔧 **[../execute-tasks-now.sql](../execute-tasks-now.sql)** - Manual task execution

### Web Interfaces
- 🍷 **Grafana**: http://localhost:3000 (admin/admin)
- 📊 **RedPanda Console**: http://localhost:8080
- 📈 **Prometheus**: http://localhost:9090
- 🔍 **Consumer Metrics**: http://localhost:8000/metrics

---

## 📞 Support

If you encounter issues:
1. Check the "Common Issues" section in [README-DEPLOYMENT.md](./README-DEPLOYMENT.md)
2. Check logs: `docker logs consumer --tail 100`
3. Verify task status in Snowflake

---

**🍷 Happy development with Les Caves d'Albert! 🍷**
