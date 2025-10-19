# 🚀 Streaming - Les Caves d'Albert

Ce dossier contient le **système de streaming en temps réel** pour l'ingestion d'événements de vente de vin via Kafka → Snowflake.

---

## 📋 Contenu

### Fichiers Python

#### `kafka_producer.py`
**Générateur d'événements de vente en temps réel**

- **Objectif**: Produire des événements de vente réalistes vers Kafka topic `sales_events`
- **Technologies**: Python, kafka-python
- **Types d'événements**:
  - `ORDER_CREATED` (70%): Commandes clients avec détails produit 🛒
  - `INVENTORY_ADJUSTED` (30%): Ajustements de stock 📦
- **Features**:
  - Emojis par catégorie (🍷 Rouge, 🥂 Blanc, 🌸 Rosé, 🍾 Effervescent, 🥃 Spiritueux)
  - Noms de produits français (Merlot, Chardonnay, etc.)
  - Logique de pricing avec réductions (25% chance)
  - Tracking d'entrepôt pour ajustements
  - Génération consistante via seeding (product_id-based)

**Configuration**:
```python
EVENT_GENERATION_DELAY = 1  # 1 événement/seconde
ORDER_CREATED_PROBABILITY = 0.7  # 70% orders, 30% inventory
PRODUCT_ID_RANGE = (1000, 1049)  # 50 produits
CUSTOMER_ID_RANGE = (1, 150)  # 150 clients
```

**Exemple d'événement ORDER_CREATED**:
```json
{
  "order_line_id": 67890,
  "customer_id": 42,
  "product_id": 1015,
  "product_name": "Chardonnay Réserve 🥂",
  "category": "Blanc",
  "quantity": 6,
  "unit_price": 18.50,
  "discount": 0.15,
  "total_price": 94.35,
  "bottle_size_liters": 0.75,
  "sales_channel": "E-com"
}
```

#### `kafka_consumer_snowflake.py`
**Consommateur Kafka → Snowflake avec monitoring Prometheus**

- **Objectif**: Ingérer les événements Kafka vers Snowflake table `RAW_EVENTS_STREAM`
- **Architecture**: ELT (Event, Load, Transform)
- **Technologies**: Python, kafka-python, snowflake-sqlalchemy, prometheus-client
- **Features**:
  - 11 métriques Prometheus (counters, histograms, gauges)
  - Validation de schéma par type d'événement
  - Dead Letter Queue (DLQ) pour événements invalides
  - Batch processing (100 events/batch)
  - Monitoring de la table de staging
  - Graceful shutdown (SIGINT/SIGTERM)
  - Statistiques de session (running totals)

**Métriques Prometheus** (exposées sur port 8000):
```
kafka_events_consumed_total         # Total events read
kafka_events_inserted_snowflake_total  # Total inserted
kafka_events_dlq_total              # Invalid events
kafka_batch_size                    # Batch distribution
kafka_batch_processing_duration_seconds  # Processing time
snowflake_insert_duration_seconds   # Snowflake insert time
kafka_current_batch_size            # Current batch gauge
kafka_snowflake_insert_rows         # Last insert count
kafka_consumer_lag                  # Consumer lag
kafka_event_size_bytes              # Event size distribution
```

#### `requirements-consumer.txt`
**Dépendances Python**

```
kafka-python==2.0.2
sqlalchemy==1.4.46
snowflake-sqlalchemy==1.4.7
pandas==2.0.3
prometheus-client==0.17.1
python-dotenv==1.0.0
```

---

## 🏗️ Architecture

```
┌─────────────────────┐
│  kafka_producer.py  │  Génère événements (ORDER_CREATED, INVENTORY_ADJUSTED)
└──────────┬──────────┘
           │ events/sec
           ▼
┌─────────────────────┐
│   RedPanda Kafka    │  Topic: sales_events (port 19092)
│   (Docker)          │
└──────────┬──────────┘
           │ batch of 100
           ▼
┌─────────────────────┐
│kafka_consumer_      │  Validation → Snowflake → Metrics
│snowflake.py         │
└──────────┬──────────┘
           │
           ├────────────────────────┐
           ▼                        ▼
┌─────────────────────┐    ┌──────────────────┐
│   Snowflake         │    │  Prometheus      │
│ RAW_EVENTS_STREAM   │    │  (port 9090)     │
└─────────────────────┘    └────────┬─────────┘
                                    ▼
                           ┌──────────────────┐
                           │    Grafana       │
                           │  (port 3000)     │
                           └──────────────────┘
```

---

## 🚀 Utilisation

### Avec Docker (Recommandé)

**1. Démarrer le stack complet**:
```bash
# Depuis la racine du projet
docker-compose up -d
```

Cela démarre:
- RedPanda (Kafka) sur port 19092
- RedPanda Console sur port 8080
- Producer (génère événements)
- Consumer (ingère vers Snowflake + expose métriques port 8000)

**2. Démarrer le monitoring**:
```bash
docker-compose -f docker-compose-monitoring.yml up -d
```

Cela démarre:
- Prometheus sur port 9090
- Grafana sur port 3000 (admin/admin123)

**3. Vérifier les logs**:
```bash
docker logs producer -f   # Voir événements générés
docker logs consumer -f   # Voir ingestion Snowflake
```

---

### Localement (Développement)

**1. Installer les dépendances**:
```bash
cd streaming
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements-consumer.txt
```

**2. Configurer l'environnement**:

Créer `.env` à la racine du projet:
```bash
# Kafka
KAFKA_TOPIC_NAME=sales_events

# Snowflake
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account.region
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=WINE_SALES_DB
SNOWFLAKE_SCHEMA=RAW_DATA
```

**3. Démarrer RedPanda** (si pas Docker Compose):
```bash
docker run -d --name redpanda \
  -p 19092:19092 -p 9644:9644 \
  docker.redpanda.com/redpandadata/redpanda:latest \
  redpanda start --smp 1 --overprovisioned --node-id 0 \
  --kafka-addr INTERNAL://0.0.0.0:9092,OUTSIDE://0.0.0.0:19092 \
  --advertise-kafka-addr INTERNAL://redpanda:9092,OUTSIDE://localhost:19092
```

**4. Lancer le producer**:
```bash
python kafka_producer.py
```

Logs:
```
🚀 Kafka Producer started - Topic: sales_events
🛒 [ORDER_CREATED] Event 1 sent | Product: Merlot Tradition 🍷 | Customer: 42
📦 [INVENTORY_ADJUSTED] Event 2 sent | Product: Chardonnay 🥂 | Warehouse: Paris
```

**5. Lancer le consumer** (dans un autre terminal):
```bash
python kafka_consumer_snowflake.py
```

Logs:
```
🚀 Starting Kafka Consumer for Snowflake ingestion
✅ Connected to Snowflake: WINE_SALES_DB.RAW_DATA
📊 Events consumed: 100 | Inserted: 98 | DLQ: 2 | Total: 100
```

**6. Vérifier les métriques**:
```bash
curl http://localhost:8000/metrics
```

---

## 📊 Schéma Snowflake

```sql
-- Table créée automatiquement par le consumer
CREATE TABLE IF NOT EXISTS RAW_EVENTS_STREAM (
    EVENT_TYPE VARCHAR(50),        -- 'ORDER_CREATED', 'INVENTORY_ADJUSTED'
    PRODUCT_ID INTEGER,             -- Index pour analytics produit
    CUSTOMER_ID INTEGER,            -- Index pour analytics client
    EVENT_METADATA OBJECT,          -- Métadonnées (timestamp, source, etc.)
    EVENT_CONTENT VARIANT,          -- JSON complet de l'événement
    INGESTION_TIME TIMESTAMP_LTZ    -- Timestamp d'ingestion automatique
);

-- Table de staging (temporaire, doit rester vide)
CREATE TABLE IF NOT EXISTS stg_raw_events_stream (
    EVENT_TYPE VARCHAR(50),
    PRODUCT_ID INTEGER,
    CUSTOMER_ID INTEGER,
    EVENT_METADATA OBJECT,
    EVENT_CONTENT VARIANT
);
```

### Requêtes d'analyse

```sql
-- Top 10 produits vendus
SELECT 
    PARSE_JSON(EVENT_CONTENT):product_name::STRING as product,
    COUNT(*) as orders,
    SUM(PARSE_JSON(EVENT_CONTENT):total_price::DECIMAL(10,2)) as revenue
FROM RAW_EVENTS_STREAM
WHERE EVENT_TYPE = 'ORDER_CREATED'
GROUP BY 1
ORDER BY revenue DESC
LIMIT 10;

-- Ventes par canal sur les dernières 24h
SELECT 
    PARSE_JSON(EVENT_CONTENT):sales_channel::STRING as channel,
    COUNT(*) as orders,
    AVG(PARSE_JSON(EVENT_CONTENT):total_price::DECIMAL(10,2)) as avg_order
FROM RAW_EVENTS_STREAM
WHERE EVENT_TYPE = 'ORDER_CREATED'
  AND INGESTION_TIME >= DATEADD(hour, -24, CURRENT_TIMESTAMP())
GROUP BY 1;

-- Ajustements d'inventaire par type
SELECT 
    PARSE_JSON(EVENT_CONTENT):adjustment_type::STRING as type,
    COUNT(*) as adjustments,
    SUM(PARSE_JSON(EVENT_CONTENT):quantity_change::INTEGER) as total_quantity
FROM RAW_EVENTS_STREAM
WHERE EVENT_TYPE = 'INVENTORY_ADJUSTED'
GROUP BY 1;
```

---

## 📈 Monitoring Grafana

**Dashboard URL**: [http://localhost:3000/d/kafka-consumer-snowflake](http://localhost:3000/d/kafka-consumer-snowflake)

**8 Panels**:
1. **Events Consumed Rate** - Timeseries du débit d'ingestion
2. **Total Events Consumed** - Compteur cumulé
3. **Current Batch Size** - Taille du batch actuel
4. **Batch Processing Duration** - p50 et p95 percentiles
5. **Snowflake Insert Duration** - p50 et p95 percentiles
6. **Events Inserted to Snowflake** - Rate d'insertion
7. **DLQ Messages** - Événements invalides (erreurs)
8. **Events Summary** - Table récapitulative par type

---

## 🔄 Différence Batch vs Streaming

| Aspect | Streaming (ce dossier) | Batch (`/batch-ingestion`) |
|--------|------------------------|----------------------------|
| **Latence** | < 1 seconde | Minutes à heures |
| **Volume** | Événement par événement | Bulk (milliers de lignes) |
| **Source** | Kafka topic `sales_events` | SQLite `wine_data.db` |
| **Destination** | `RAW_DATA.RAW_EVENTS_STREAM` | `BATCH_DATA.sales` |
| **Monitoring** | Prometheus + Grafana | Logs notebook |
| **Use Case** | Analytics temps réel | Chargement historique |

---

## 🛠️ Troubleshooting

**Problème**: Producer ne peut pas se connecter à Kafka
```
✅ Vérifier que RedPanda est démarré: docker ps | grep redpanda
✅ Tester la connexion: telnet localhost 19092
```

**Problème**: Consumer erreur "Invalid credentials" Snowflake
```
✅ Vérifier .env avec les bons credentials
✅ Tester: snowsql -a <account> -u <user>
```

**Problème**: Pas de métriques dans Grafana
```
✅ Vérifier consumer expose metrics: curl http://localhost:8000/metrics
✅ Vérifier Prometheus scrape: http://localhost:9090/targets
✅ Vérifier dashboard JSON est bien chargé
```

**Problème**: Table stg_raw_events_stream contient des données
```
✅ Le consumer log un WARNING au démarrage si non vide
✅ C'est une table temporaire pour pandas→Snowflake, doit s'auto-nettoyer
✅ Si persiste: TRUNCATE TABLE stg_raw_events_stream;
```

---

## 📚 Documentation Complète

- **[KAFKA_PRODUCER_IMPROVEMENTS.md](../KAFKA_PRODUCER_IMPROVEMENTS.md)**: Détails des améliorations producer
- **[KAFKA_CONSUMER_README.md](../KAFKA_CONSUMER_README.md)**: Documentation technique consumer (3500 mots)
- **[QUICK_START.md](../QUICK_START.md)**: Guide opérationnel complet
- **[CONSUMER_IMPROVEMENTS.md](../CONSUMER_IMPROVEMENTS.md)**: Résumé des améliorations
- **[SAMPLE_OUTPUT.md](../SAMPLE_OUTPUT.md)**: Exemples de logs et JSON

---

**Pour l'ingestion batch historique, voir le dossier `/batch-ingestion` 📦**
