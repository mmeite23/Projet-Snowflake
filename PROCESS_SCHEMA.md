# 🔄 Process Schema - Les Caves d'Albert Event Streaming Pipeline

This document provides comprehensive visual schemas outlining all the steps and processes in the wine sales event streaming system.

---

## 📊 Table of Contents

1. [High-Level Architecture](#1-high-level-architecture)
2. [Data Flow Pipeline](#2-data-flow-pipeline)
3. [Event Processing Steps](#3-event-processing-steps)
4. [Snowflake Data Transformation](#4-snowflake-data-transformation)
5. [Monitoring & Observability](#5-monitoring--observability)
6. [Deployment Process](#6-deployment-process)

---

## 1. High-Level Architecture

```mermaid
graph TB
    subgraph "Event Generation"
        A[Producer Container] -->|Generate Events| B[Wine Sales Data]
        B -->|ORDER_CREATED| C[Kafka Topics]
        B -->|INVENTORY_ADJUSTED| C
    end
    
    subgraph "Stream Processing"
        C -->|Subscribe| D[RedPanda Broker]
        D -->|Partition Management| E[Consumer Group]
    end
    
    subgraph "Data Ingestion"
        E -->|Batch Processing| F[Consumer Container]
        F -->|Batch Size: 100| G[Snowflake Connection]
        G -->|Insert| H[RAW Schema]
    end
    
    subgraph "Data Warehouse - Snowflake"
        H[RAW_ORDERS] -->|Stream| I[STAGING Schema]
        I[STAGING_ORDERS] -->|Task/ELT| J[PRODUCTION Schema]
        J[PROD_ORDERS] -->|Aggregations| K[Analytics Views]
    end
    
    subgraph "Monitoring Stack"
        F -->|Expose Metrics| L[Prometheus]
        L -->|Scrape :8000/metrics| M[Grafana Dashboards]
        D -->|JMX Metrics| L
    end
    
    subgraph "Business Intelligence"
        J -->|Query| N[Streamlit Dashboard]
        K -->|KPIs| N
        N -->|Real-time Viz| O[End Users]
    end
    
    style A fill:#ff6b6b
    style D fill:#4ecdc4
    style H fill:#45b7d1
    style J fill:#96ceb4
    style L fill:#ffeaa7
    style N fill:#fd79a8
```

---

## 2. Data Flow Pipeline

### Complete End-to-End Process

```mermaid
sequenceDiagram
    participant P as Producer
    participant K as RedPanda (Kafka)
    participant C as Consumer
    participant S as Snowflake
    participant M as Monitoring
    participant D as Dashboard
    
    Note over P: Step 1: Event Generation
    P->>P: Load wine catalog (300+ products)
    P->>P: Generate random customer data
    P->>P: Create ORDER_CREATED event
    P->>K: Publish to topic
    
    Note over K: Step 2: Stream Buffering
    K->>K: Store in partition
    K->>K: Maintain offset
    
    Note over C: Step 3: Consumption
    C->>K: Poll events (batch=100)
    K-->>C: Return event batch
    C->>C: Deserialize JSON
    C->>C: Validate schema
    
    Note over C,S: Step 4: Batch Ingestion
    C->>S: Execute INSERT query
    S->>S: Write to RAW_ORDERS table
    S-->>C: Commit confirmation
    C->>K: Commit offset
    
    Note over S: Step 5: ELT Processing
    S->>S: Stream detects change
    S->>S: Task executes transformation
    S->>S: Insert into STAGING
    S->>S: Insert into PRODUCTION
    
    Note over M: Step 6: Metrics Collection
    C->>M: Push metrics (:8000/metrics)
    M->>M: Scrape & store time-series
    
    Note over D: Step 7: Visualization
    D->>S: Query PRODUCTION tables
    S-->>D: Return aggregated data
    D->>M: Query metrics
    M-->>D: Return performance data
    D->>D: Render dashboards
```

---

## 3. Event Processing Steps

### Detailed Consumer Processing Flow

```mermaid
flowchart TD
    Start([Consumer Starts]) --> Init[Initialize Kafka Consumer]
    Init --> Config[Load Configuration]
    Config --> Connect[Connect to RedPanda :9092]
    Connect --> Subscribe[Subscribe to Topics]
    Subscribe --> Loop{Polling Loop}
    
    Loop -->|Poll| Fetch[Fetch Batch of Events]
    Fetch --> Check{Events Received?}
    Check -->|No| Loop
    Check -->|Yes| Parse[Parse JSON Events]
    
    Parse --> Validate[Validate Event Schema]
    Validate --> Valid{Valid?}
    Valid -->|No| Error1[Log Error]
    Error1 --> Metrics1[Increment Error Counter]
    Metrics1 --> Loop
    
    Valid -->|Yes| Categorize{Event Type?}
    Categorize -->|ORDER_CREATED| OrderBuffer[Add to Orders Buffer]
    Categorize -->|INVENTORY_ADJUSTED| InvBuffer[Add to Inventory Buffer]
    Categorize -->|Other| OtherBuffer[Add to Other Buffer]
    
    OrderBuffer --> BatchCheck{Batch Size >= 100?}
    InvBuffer --> BatchCheck
    OtherBuffer --> BatchCheck
    
    BatchCheck -->|No| Loop
    BatchCheck -->|Yes| SnowConnect[Connect to Snowflake]
    
    SnowConnect --> Insert[Execute Batch INSERT]
    Insert --> InsertCheck{Success?}
    
    InsertCheck -->|No| Retry[Retry Logic]
    Retry --> RetryCount{Retry < 3?}
    RetryCount -->|Yes| Insert
    RetryCount -->|No| Error2[Log Critical Error]
    Error2 --> Metrics2[Update Metrics]
    Metrics2 --> Loop
    
    InsertCheck -->|Yes| Commit[Commit Kafka Offset]
    Commit --> UpdateMetrics[Update Success Metrics]
    UpdateMetrics --> ClearBuffer[Clear Batch Buffer]
    ClearBuffer --> ExposeMetrics[Expose Prometheus Metrics]
    ExposeMetrics --> Loop
    
    Loop -->|Shutdown Signal| Cleanup[Cleanup Resources]
    Cleanup --> End([Consumer Stops])
    
    style Start fill:#90EE90
    style End fill:#FFB6C1
    style Error1 fill:#FF6B6B
    style Error2 fill:#FF6B6B
    style Insert fill:#4ECDC4
    style ExposeMetrics fill:#FFEAA7
```

---

## 4. Snowflake Data Transformation

### ELT Pipeline in Snowflake

```mermaid
flowchart LR
    subgraph "RAW Layer"
        A[RAW_ORDERS] -->|Change Detection| B[Stream: ORDER_STREAM]
        C[RAW_INVENTORY] -->|Change Detection| D[Stream: INVENTORY_STREAM]
    end
    
    subgraph "STAGING Layer"
        B -->|Task: LOAD_STAGING_ORDERS| E[STAGING_ORDERS]
        D -->|Task: LOAD_STAGING_INVENTORY| F[STAGING_INVENTORY]
        E -->|Data Cleansing| E1[Remove Duplicates]
        E1 -->|Validation| E2[Type Casting]
        F -->|Data Cleansing| F1[Normalize Values]
    end
    
    subgraph "PRODUCTION Layer"
        E2 -->|Task: LOAD_PROD_ORDERS| G[PROD_ORDERS]
        F1 -->|Task: LOAD_PROD_INVENTORY| H[PROD_INVENTORY]
        G -->|Enrichment| G1[Add Calculated Fields]
        H -->|Aggregation| H1[Stock Levels]
    end
    
    subgraph "Analytics Layer"
        G1 --> I[VIEW: DAILY_SALES]
        G1 --> J[VIEW: CUSTOMER_METRICS]
        H1 --> K[VIEW: INVENTORY_STATUS]
        G1 --> L[VIEW: PRODUCT_PERFORMANCE]
    end
    
    subgraph "Automation"
        M[Task: REFRESH_ANALYTICS] -->|Schedule: 5min| I
        M -->|Schedule: 5min| J
        M -->|Schedule: 5min| K
        M -->|Schedule: 5min| L
    end
    
    style A fill:#FFE5E5
    style E fill:#FFF5E5
    style G fill:#E5F5E5
    style I fill:#E5E5FF
```

### Snowflake Task Execution Schedule

```mermaid
gantt
    title Snowflake Tasks Execution Timeline
    dateFormat HH:mm
    axisFormat %H:%M
    
    section Data Ingestion
    Consumer Batch Insert (RAW) :active, raw1, 00:00, 3m
    Consumer Batch Insert (RAW) :raw2, 00:05, 3m
    Consumer Batch Insert (RAW) :raw3, 00:10, 3m
    
    section Staging Tasks
    LOAD_STAGING_ORDERS :staging1, 00:03, 2m
    LOAD_STAGING_INVENTORY :staging2, 00:03, 2m
    LOAD_STAGING_ORDERS :staging3, 00:08, 2m
    LOAD_STAGING_INVENTORY :staging4, 00:08, 2m
    
    section Production Tasks
    LOAD_PROD_ORDERS :prod1, 00:05, 2m
    LOAD_PROD_INVENTORY :prod2, 00:05, 2m
    LOAD_PROD_ORDERS :prod3, 00:10, 2m
    LOAD_PROD_INVENTORY :prod4, 00:10, 2m
    
    section Analytics Refresh
    REFRESH_ANALYTICS :analytics1, 00:07, 1m
    REFRESH_ANALYTICS :analytics2, 00:12, 1m
```

---

## 5. Monitoring & Observability

### Metrics Collection Flow

```mermaid
flowchart TB
    subgraph "Application Layer"
        A[Consumer Process] -->|Expose| B[HTTP Endpoint :8000/metrics]
        C[Producer Process] -->|Generate| D[Application Logs]
        E[RedPanda Broker] -->|JMX Exporter| F[Kafka Metrics]
    end
    
    subgraph "Collection Layer"
        B -->|Scrape every 15s| G[Prometheus Server]
        F -->|Scrape every 15s| G
        D -->|Parse| H[Log Aggregator]
    end
    
    subgraph "Storage Layer"
        G -->|Time-Series DB| I[Prometheus TSDB]
        I -->|Retention: 15d| I
    end
    
    subgraph "Visualization Layer"
        I -->|PromQL Query| J[Grafana Dashboards]
        J --> K[Consumer Performance Panel]
        J --> L[Kafka Metrics Panel]
        J --> M[System Resources Panel]
        J --> N[Alerts Panel]
    end
    
    subgraph "Alerting Layer"
        N -->|Threshold Exceeded| O[Alert Manager]
        O -->|Notify| P[Email/Slack/PagerDuty]
    end
    
    style A fill:#FF6B6B
    style G fill:#FFEAA7
    style J fill:#96CEB4
    style O fill:#FF7675
```

### Key Metrics Exposed

```mermaid
mindmap
    root((Prometheus Metrics))
        Consumer Metrics
            events_consumed_total
            events_processed_total
            batch_processing_seconds
            batch_size_events
            kafka_lag_messages
            snowflake_insert_errors
        Producer Metrics
            events_produced_total
            event_type_counter
            producer_latency_ms
        RedPanda Metrics
            kafka_broker_health
            partition_count
            consumer_group_lag
            message_throughput
        System Metrics
            cpu_usage_percent
            memory_usage_mb
            disk_io_operations
            network_bytes_sent
```

---

## 6. Deployment Process

### Docker Compose Orchestration

```mermaid
flowchart TD
    Start([docker-compose up]) --> Parse[Parse YAML Configuration]
    Parse --> Network[Create Docker Network: kafka-network]
    Network --> Volumes[Create Persistent Volumes]
    
    Volumes --> RedPanda[Start RedPanda Container]
    RedPanda --> RPWait{RedPanda Ready?}
    RPWait -->|No| RPWait
    RPWait -->|Yes| Console[Start RedPanda Console]
    
    Console --> Producer[Start Producer Container]
    Producer --> ProdInit[Initialize Wine Catalog]
    ProdInit --> ProdLoop[Start Event Generation Loop]
    
    RPWait -->|Yes| Consumer[Start Consumer Container]
    Consumer --> ConsInit[Initialize Kafka Consumer]
    ConsInit --> ConsConnect[Connect to RedPanda]
    ConsConnect --> ConsSnow[Connect to Snowflake]
    ConsSnow --> ConsLoop[Start Polling Loop]
    
    Console --> Prometheus[Start Prometheus]
    Prometheus --> PromConfig[Load prometheus.yml]
    PromConfig --> PromScrape[Start Scraping Targets]
    
    Prometheus --> Grafana[Start Grafana]
    Grafana --> GrafConfig[Load Provisioning]
    GrafConfig --> GrafDash[Import Dashboards]
    GrafDash --> GrafReady[Expose Port :3000]
    
    ProdLoop --> Running{All Services Up?}
    ConsLoop --> Running
    PromScrape --> Running
    GrafReady --> Running
    
    Running -->|Yes| Monitor[Monitor Health]
    Monitor --> Check{Check Status}
    Check -->|Healthy| Monitor
    Check -->|Issue Detected| Alert[Trigger Alert]
    Alert --> Investigate[Investigate Logs]
    Investigate --> Fix[Apply Fix]
    Fix --> Restart[Restart Service if Needed]
    Restart --> Monitor
    
    Running -->|Shutdown Signal| Graceful[Graceful Shutdown]
    Graceful --> StopCons[Stop Consumer - Commit Offsets]
    StopCons --> StopProd[Stop Producer]
    StopProd --> StopMon[Stop Monitoring Stack]
    StopMon --> StopRP[Stop RedPanda]
    StopRP --> Cleanup[Remove Containers]
    Cleanup --> End([Deployment Complete])
    
    style Start fill:#90EE90
    style Running fill:#4ECDC4
    style Monitor fill:#FFEAA7
    style Alert fill:#FF6B6B
    style End fill:#FFB6C1
```

---

## 📋 Process Summary

### Step-by-Step Execution

| Step | Component | Action | Duration | Output |
|------|-----------|--------|----------|--------|
| 1 | **Producer** | Generate wine sales events | Continuous | JSON events |
| 2 | **RedPanda** | Buffer events in topics | Real-time | Partitioned messages |
| 3 | **Consumer** | Poll and batch events | ~3s/batch | 100 events buffered |
| 4 | **Consumer** | Validate and parse JSON | <100ms | Structured data |
| 5 | **Consumer** | Insert batch to Snowflake RAW | ~2-3s | RAW_ORDERS populated |
| 6 | **Snowflake Stream** | Detect new records | Real-time | Change data capture |
| 7 | **Snowflake Task** | Transform RAW → STAGING | 1-5min | STAGING_ORDERS populated |
| 8 | **Snowflake Task** | Transform STAGING → PROD | 1-5min | PROD_ORDERS populated |
| 9 | **Prometheus** | Scrape metrics endpoint | Every 15s | Time-series data |
| 10 | **Grafana** | Query and visualize metrics | Real-time | Dashboard refresh |
| 11 | **Streamlit** | Query production tables | On-demand | BI analytics |

---

## 🔍 Data Lineage

```mermaid
graph LR
    A[Source: Producer] -->|Raw Events| B[Bronze: RAW Schema]
    B -->|Stream Detection| C[Silver: STAGING Schema]
    C -->|Business Logic| D[Gold: PRODUCTION Schema]
    D -->|Aggregations| E[Platinum: Analytics Views]
    E -->|Visualization| F[End User: Dashboard]
    
    style A fill:#8B4513
    style B fill:#CD7F32
    style C fill:#C0C0C0
    style D fill:#FFD700
    style E fill:#E5E4E2
    style F fill:#00CED1
```

---

## ✅ Process Validation Checklist

- [x] **Event Generation**: Producer generates realistic events with French wine data
- [x] **Stream Buffering**: RedPanda manages topics and partitions
- [x] **Batch Processing**: Consumer processes 100 events per batch
- [x] **Data Validation**: Schema validation before Snowflake insertion
- [x] **ELT Pipeline**: Automated transformation through RAW → STAGING → PRODUCTION
- [x] **Monitoring**: Real-time metrics exposed to Prometheus
- [x] **Visualization**: Grafana dashboards display pipeline health
- [x] **Analytics**: Streamlit dashboard queries production data
- [x] **Error Handling**: Retry logic and error logging implemented
- [x] **Observability**: Comprehensive logging at each step

---

**Document Version**: 1.0  
**Last Updated**: October 19, 2025  
**Author**: Mory Junior MEITE  
**Project**: Les Caves d'Albert - Event Streaming Pipeline
