# 🐳 Docker Configuration

Docker Compose files and Dockerfile for **Les Caves d'Albert** infrastructure.

## 📁 Files

```
docker/
├── docker-compose.yml              # Main application stack
├── docker-compose-monitoring.yml   # Monitoring stack (Prometheus + Grafana)
└── Dockerfile                      # Consumer container image
```

## 🚀 Quick Start

### Start All Services

```bash
# From project root
cd /path/to/Projet-Snowflake

# Start main application stack
docker compose -f docker/docker-compose.yml up -d

# Start monitoring stack
docker compose -f docker/docker-compose-monitoring.yml up -d

# Check all containers
docker ps
```

## 📦 Main Application Stack

### Services Included

| Service | Port | Description |
|---------|------|-------------|
| **redpanda** | 9092, 8080 | Kafka-compatible event streaming |
| **redpanda-console** | 8080 | Web UI for Kafka management |
| **producer** | - | Generates wine sales events |
| **consumer** | 8000 | Ingests events to Snowflake |

### Environment Variables

Create `.env` file in project root:

```bash
# Kafka Configuration
KAFKA_TOPIC_NAME=sales_events
KAFKA_BOOTSTRAP_SERVER=redpanda:9092

# Snowflake Configuration
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=CAVES_ALBERT_DB
SNOWFLAKE_SCHEMA=RAW_DATA

# Consumer Configuration
BATCH_SIZE=100
COMMIT_INTERVAL_SECONDS=10
METRICS_PORT=8000
```

### Commands

```bash
# Start services
docker compose -f docker/docker-compose.yml up -d

# View logs
docker compose -f docker/docker-compose.yml logs -f

# Check specific service logs
docker compose -f docker/docker-compose.yml logs -f consumer

# Stop services
docker compose -f docker/docker-compose.yml down

# Restart a service
docker compose -f docker/docker-compose.yml restart consumer

# Rebuild and restart
docker compose -f docker/docker-compose.yml up -d --build
```

## 📈 Monitoring Stack

### Services Included

| Service | Port | Credentials | Description |
|---------|------|-------------|-------------|
| **prometheus** | 9090 | - | Metrics collection |
| **grafana** | 3000 | admin/admin | Visualization |

### Commands

```bash
# Start monitoring
docker compose -f docker/docker-compose-monitoring.yml up -d

# View logs
docker compose -f docker/docker-compose-monitoring.yml logs -f

# Stop monitoring
docker compose -f docker/docker-compose-monitoring.yml down
```

## 🔧 Configuration

### Modify Consumer Batch Size

Edit `docker-compose.yml`:
```yaml
consumer:
  environment:
    - BATCH_SIZE=200  # Default: 100
```

### Add New Service

Edit `docker-compose.yml`:
```yaml
services:
  # ... existing services ...
  
  my-new-service:
    image: my-image:latest
    ports:
      - "8081:8080"
    environment:
      - MY_VAR=value
    networks:
      - kafka-network
```

### Change Network Configuration

```yaml
networks:
  kafka-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

## 🛠️ Dockerfile

Builds the Kafka consumer container:

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY streaming/kafka_consumer_snowflake.py .
CMD ["python", "kafka_consumer_snowflake.py"]
```

### Build Custom Image

```bash
# Build image
docker build -f docker/Dockerfile -t les-caves-albert-consumer:latest .

# Run container
docker run -d \
  --name consumer \
  --env-file .env \
  -p 8000:8000 \
  les-caves-albert-consumer:latest
```

## 🔍 Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose -f docker/docker-compose.yml logs consumer

# Check if ports are already in use
lsof -i :9092  # RedPanda
lsof -i :8000  # Consumer metrics

# Remove and recreate
docker compose -f docker/docker-compose.yml down -v
docker compose -f docker/docker-compose.yml up -d
```

### Consumer Not Connecting to Snowflake

```bash
# Check environment variables
docker compose -f docker/docker-compose.yml exec consumer env | grep SNOWFLAKE

# Test Snowflake connection
docker compose -f docker/docker-compose.yml exec consumer python -c "
import snowflake.connector
conn = snowflake.connector.connect(
    user='$SNOWFLAKE_USER',
    password='$SNOWFLAKE_PASSWORD',
    account='$SNOWFLAKE_ACCOUNT'
)
print('✅ Connection successful')
"
```

### RedPanda Issues

```bash
# Check RedPanda logs
docker compose -f docker/docker-compose.yml logs redpanda

# List topics
docker compose -f docker/docker-compose.yml exec redpanda \
  rpk topic list

# Check consumer groups
docker compose -f docker/docker-compose.yml exec redpanda \
  rpk group list
```

## 📊 Resource Limits

### Modify Resource Constraints

Edit `docker-compose.yml`:
```yaml
consumer:
  deploy:
    resources:
      limits:
        cpus: '2.0'
        memory: 2G
      reservations:
        cpus: '0.5'
        memory: 512M
```

## 🔗 Related Documentation

- [README-DEPLOYMENT.md](../documentation/README-DEPLOYMENT.md) - Complete deployment guide
- [QUICK_START.md](../documentation/QUICK_START.md) - Quick start guide
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

---

**🍷 Les Caves d'Albert** - Docker Configuration
