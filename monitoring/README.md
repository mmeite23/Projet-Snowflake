# 📈 Monitoring Stack

Prometheus + Grafana monitoring for **Les Caves d'Albert** data pipeline.

## 📁 Structure

```
monitoring/
├── prometheus.yml                          # Prometheus configuration
├── grafana/
│   └── dashboards/
│       └── grafana-dashboard-consumer.json # Consumer metrics dashboard
└── grafana-provisioning/
    ├── dashboards/
    │   └── dashboard.yml                   # Dashboard provisioning
    └── datasources/
        └── prometheus.yml                  # Prometheus datasource
```

## 🎯 Components

### Prometheus
- **Port**: `9090`
- **Scrape Interval**: 15s
- **Targets**:
  - Kafka Consumer (`host.docker.internal:8000`)
  - Prometheus itself

### Grafana
- **Port**: `3000`
- **Credentials**: `admin` / `admin`
- **Dashboards**: 1 pre-configured (Consumer Metrics)
- **Datasources**: Prometheus (auto-provisioned)

## 🚀 Quick Start

### Start Monitoring Stack

```bash
# From project root
docker compose -f docker/docker-compose-monitoring.yml up -d

# Check containers
docker compose -f docker/docker-compose-monitoring.yml ps

# View logs
docker compose -f docker/docker-compose-monitoring.yml logs -f
```

### Access Interfaces

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000
  - Username: `admin`
  - Password: `admin`

## 📊 Metrics Available

### Kafka Consumer Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `kafka_events_consumed_total` | Counter | Total events consumed |
| `kafka_events_processed_total` | Counter | Events processed successfully |
| `snowflake_inserts_total` | Counter | Records inserted to Snowflake |
| `batch_processing_duration_seconds` | Histogram | Batch processing time |
| `dlq_messages_total` | Counter | Dead letter queue messages |
| `kafka_lag` | Gauge | Consumer lag |
| `active_partitions` | Gauge | Active Kafka partitions |
| `snowflake_connection_errors` | Counter | Connection errors |
| `memory_usage_bytes` | Gauge | Memory usage |
| `cpu_usage_percent` | Gauge | CPU usage |
| `process_uptime_seconds` | Gauge | Process uptime |

### Prometheus Queries Examples

```promql
# Events consumed per second
rate(kafka_events_consumed_total{status="success"}[1m])

# Average batch processing time
rate(batch_processing_duration_seconds_sum[5m]) / rate(batch_processing_duration_seconds_count[5m])

# Error rate
rate(dlq_messages_total[5m])

# Consumer lag
kafka_lag
```

## 📊 Grafana Dashboard

### Panels Included

1. **Events Consumed** - Total events ingested
2. **Processing Rate** - Events per second
3. **Batch Processing Time** - P50, P95, P99 latencies
4. **Error Rate** - DLQ messages over time
5. **Snowflake Inserts** - Records written to Snowflake
6. **Consumer Lag** - Kafka partition lag
7. **Resource Usage** - CPU & Memory
8. **Uptime** - Service availability

### Import Dashboard

The dashboard is auto-provisioned on startup. To manually import:

1. Open Grafana → Dashboards → Import
2. Upload `grafana/dashboards/grafana-dashboard-consumer.json`
3. Select Prometheus datasource
4. Click **Import**

## 🔧 Configuration

### Modify Scrape Targets

Edit `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'kafka-consumer-snowflake'
    static_configs:
      - targets: ['host.docker.internal:8000']
    scrape_interval: 15s  # Change this
```

### Add New Dashboard

1. Create dashboard in Grafana UI
2. Export as JSON
3. Save to `grafana/dashboards/`
4. Restart Grafana container

### Change Grafana Password

```bash
# Stop Grafana
docker compose -f docker/docker-compose-monitoring.yml stop grafana

# Remove volume (resets password)
docker volume rm projet-snowflake_grafana-storage

# Restart
docker compose -f docker/docker-compose-monitoring.yml up -d grafana
```

## 🛑 Stop Monitoring

```bash
# Stop containers
docker compose -f docker/docker-compose-monitoring.yml down

# Stop and remove volumes (data loss!)
docker compose -f docker/docker-compose-monitoring.yml down -v
```

## 📖 Documentation

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Project Monitoring Guide](../documentation/README-DEPLOYMENT.md#monitoring)

---

**🍷 Les Caves d'Albert** - Monitoring Stack
