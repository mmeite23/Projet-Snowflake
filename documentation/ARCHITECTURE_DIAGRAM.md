# 🍷 Architecture Snowflake Tasks & Streams - Les Caves d'Albert

## Flux de données complet

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                    🔴 KAFKA STREAMING LAYER                      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
         │                                      │
         ↓                                      ↓
   kafka_producer.py                     RedPanda Cluster
   (1 event/sec)                         (Topic: sales_events)
         │                                      │
         └──────────────────┬───────────────────┘
                           ↓
                  kafka_consumer_snowflake.py
                  (Batch: 60 sec / 50 events)
                           │
                           ↓
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                    ❄️  SNOWFLAKE - LAYER 1: RAW (BRONZE)        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

    ┌─────────────────────────────────────────────────────────┐
    │  📦 RAW_EVENTS_STREAM                                   │
    │  ├── EVENT_ID (VARCHAR)                                 │
    │  ├── EVENT_TYPE (VARCHAR)                               │
    │  │   - "ORDER_CREATED" (70%)                            │
    │  │   - "INVENTORY_ADJUSTED" (30%)                       │
    │  ├── EVENT_TIMESTAMP (TIMESTAMP_NTZ)                    │
    │  ├── PRODUCT_ID (VARCHAR)                               │
    │  ├── CUSTOMER_ID (VARCHAR)                              │
    │  ├── EVENT_DATA (VARIANT JSON)                          │
    │  └── INGESTION_TIMESTAMP (TIMESTAMP_NTZ)                │
    └─────────────────────────────────────────────────────────┘
                           │
         ┌─────────────────┴─────────────────┐
         │                                   │
         ↓                                   ↓
    ┌─────────────────┐              ┌─────────────────┐
    │ 🔄 STREAM       │              │ 🔄 STREAM       │
    │ RAW_ORDERS      │              │ RAW_INVENTORY   │
    │ (APPEND_ONLY)   │              │ (APPEND_ONLY)   │
    └────────┬────────┘              └────────┬────────┘
             │                                │
             ↓                                ↓
    ┌─────────────────┐              ┌─────────────────┐
    │ ⚙️ TASK 1       │              │ ⚙️ TASK 2       │
    │ RAW→STG_ORDERS  │              │ RAW→STG_INVENTORY│
    │ ⏱️  1 MINUTE    │              │ ⏱️  1 MINUTE    │
    └────────┬────────┘              └────────┬────────┘
             │                                │
             ↓                                ↓

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                  ⚙️  SNOWFLAKE - LAYER 2: STAGING (SILVER)      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

    ┌───────────────────────┐       ┌───────────────────────┐
    │ 📋 STG_ORDERS         │       │ 📦 STG_INVENTORY_ADJ  │
    │ - ORDER_ID            │       │ - ADJUSTMENT_ID       │
    │ - CUSTOMER_ID         │       │ - PRODUCT_ID          │
    │ - PRODUCT_ID          │       │ - PRODUCT_NAME        │
    │ - PRODUCT_NAME        │       │ - ADJUSTMENT_TYPE     │
    │ - PRODUCT_CATEGORY    │       │ - QUANTITY_CHANGE     │
    │ - QUANTITY            │       │ - NEW_STOCK_LEVEL     │
    │ - UNIT_PRICE          │       │ - REASON              │
    │ - TOTAL_AMOUNT        │       │ - WAREHOUSE_LOCATION  │
    │ - PAYMENT_METHOD      │       │ - INGESTION_TIMESTAMP │
    │ - SHIPPING_ADDRESS    │       └───────────┬───────────┘
    │ - INGESTION_TIMESTAMP │                   │
    └───────────┬───────────┘       ┌───────────┴───────────┐
                │                   │                       │
                ↓                   ↓                       ↓
    ┌─────────────────┐    ┌─────────────────┐  ┌─────────────────┐
    │ 🔄 STREAM       │    │ 🔄 STREAM       │  │ 🔄 STREAM       │
    │ STG_ORDERS      │    │ STG_INVENTORY   │  │ STG_INVENTORY   │
    │ (STANDARD CDC)  │    │ (STANDARD CDC)  │  │ (STANDARD CDC)  │
    └────────┬────────┘    └────────┬────────┘  └────────┬────────┘
             │                      │                     │
             ↓                      ↓                     ↓
    ┌─────────────────┐    ┌─────────────────┐  ┌─────────────────┐
    │ ⚙️ TASK 3       │    │ ⚙️ TASK 4       │  │ ⚙️ TASK 5       │
    │ STG→PROD_ORDERS │    │ STG→PROD_       │  │ STG→PROD_       │
    │                 │    │ INVENTORY_      │  │ INVENTORY_      │
    │ 🔗 AFTER Task 1 │    │ HISTORY         │  │ CURRENT         │
    │                 │    │ 🔗 AFTER Task 2 │  │ 🔗 AFTER Task 4 │
    └────────┬────────┘    └────────┬────────┘  └────────┬────────┘
             │                      │                     │
             ↓                      ↓                     ↓

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                  🏆 SNOWFLAKE - LAYER 3: PRODUCTION (GOLD)      ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│ 🛒 ORDERS            │  │ 📊 INVENTORY_CURRENT │  │ 📚 INVENTORY_HISTORY │
│ ==================== │  │ ==================== │  │ ==================== │
│ ORDER_ID (PK)        │  │ PRODUCT_ID (PK)      │  │ ADJUSTMENT_ID (PK)   │
│ ORDER_DATE           │  │ PRODUCT_NAME         │  │ ADJUSTMENT_DATE      │
│ ORDER_TIMESTAMP      │  │ PRODUCT_CATEGORY     │  │ ADJUSTMENT_TIMESTAMP │
│ CUSTOMER_ID          │  │ CURRENT_STOCK_LEVEL  │  │ PRODUCT_ID           │
│ PRODUCT_ID           │  │ LAST_ADJ_TIMESTAMP   │  │ PRODUCT_NAME         │
│ PRODUCT_NAME         │  │ WAREHOUSE_LOCATION   │  │ ADJUSTMENT_TYPE      │
│ PRODUCT_CATEGORY     │  │ UPDATED_AT           │  │ QUANTITY_CHANGE      │
│ QUANTITY             │  │                      │  │ NEW_STOCK_LEVEL      │
│ UNIT_PRICE           │  │ 🎯 État actuel       │  │ REASON               │
│ TOTAL_AMOUNT         │  │ 🎯 1 ligne/produit   │  │ WAREHOUSE_LOCATION   │
│ PAYMENT_METHOD       │  │ 🎯 MERGE (upsert)    │  │ CREATED_AT           │
│ SHIPPING_ADDRESS     │  │                      │  │                      │
│ CREATED_AT           │  │                      │  │ 🎯 Audit trail       │
│ UPDATED_AT           │  │                      │  │ 🎯 Historique complet│
│                      │  │                      │  │ 🎯 INSERT only       │
│ 🎯 Toutes commandes  │  └──────────────────────┘  └──────────────────────┘
│ 🎯 MERGE (upsert)    │
└──────────────────────┘
         │                          │                          │
         └──────────────────────────┴──────────────────────────┘
                                    │
                                    ↓
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                      📊 ANALYTICAL LAYER                         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

    ┌────────────────────────────────────────────────────────┐
    │  📈 Dashboards BI / Requêtes analytiques               │
    │  ────────────────────────────────────────────────      │
    │  • Top produits vendus                                 │
    │  • Revenus par catégorie                               │
    │  • Analyse de la fidélité clients                      │
    │  • Prévision de rupture de stock                       │
    │  • Tendances de saisonnalité                           │
    │  • Alertes stock bas                                   │
    └────────────────────────────────────────────────────────┘
```

---

## 🎯 Points clés de l'architecture

### ⚡ Performance
- **Latence totale** : < 3 minutes de bout en bout
- **Fréquence d'exécution** : Tasks toutes les 1 minute
- **Traitement par batch** : Consumer Kafka traite 50-70 événements/batch

### 💰 Optimisation des coûts
- Tasks s'exécutent uniquement si `SYSTEM$STREAM_HAS_DATA() = TRUE`
- Warehouse s'arrête automatiquement entre les exécutions
- Pas de traitement inutile = économie de crédits Snowflake

### 🔒 Fiabilité
- **CDC natif** avec Snowflake Streams (Change Data Capture)
- **Exactly-once semantics** : Chaque événement traité une seule fois
- **DAG de tasks** : Ordre d'exécution garanti avec `AFTER` clause
- **Audit trail** : Table INVENTORY_HISTORY conserve tout l'historique

### 📊 Traçabilité
- `INGESTION_TIMESTAMP` : Timestamp d'arrivée dans Snowflake
- `EVENT_TIMESTAMP` : Timestamp de génération de l'événement
- `UPDATED_AT` / `CREATED_AT` : Timestamps de traitement en production

---

## 🔄 Cycle de vie d'un événement

### Exemple : Commande ORDER_CREATED

```
T+0s   : 🏭 Producer génère l'événement
         └─→ {"order_id": "ORD-123", "product_name": "🍷 Château Margaux", ...}

T+1s   : 📨 Kafka (RedPanda) reçoit l'événement
         └─→ Topic: sales_events, Partition: 0

T+60s  : 🔄 Consumer lit le batch (50-70 événements)
         └─→ Traitement: 3.25 secondes

T+63s  : ❄️  Insertion dans RAW_EVENTS_STREAM
         └─→ EVENT_DATA contient le JSON complet

T+64s  : 🔍 STREAM_RAW_ORDERS détecte le nouvel événement
         └─→ SYSTEM$STREAM_HAS_DATA() = TRUE

T+120s : ⚙️  TASK_RAW_TO_STAGING_ORDERS s'exécute (1 min schedule)
         └─→ Extraction du JSON → STG_ORDERS

T+121s : 🔍 STREAM_STG_ORDERS détecte le nouvel enregistrement

T+122s : ⚙️  TASK_STAGING_TO_PROD_ORDERS s'exécute (AFTER parent)
         └─→ MERGE dans PRODUCTION.ORDERS

T+123s : ✅ Donnée disponible pour l'analytique !
```

**Latence totale : ~2 minutes**

---

## 📋 Checklist de déploiement

### Avant de lancer

- [ ] Base de données `CAVES_ALBERT_DB` créée
- [ ] Schémas `RAW_DATA`, `STAGING`, `PRODUCTION` créés
- [ ] Warehouse `COMPUTE_WH` disponible
- [ ] Consumer Kafka ingère des données dans `RAW_EVENTS_STREAM`
- [ ] Verify que des données sont présentes : `SELECT COUNT(*) FROM RAW_EVENTS_STREAM`

### Déploiement

1. [ ] Execute `snowflake-tasks-streams.sql` (crée tables + streams + tasks)
2. [ ] Verify que les streams sont créés : `SHOW STREAMS`
3. [ ] Verify que les tasks sont actives : `SHOW TASKS` → `STATE = 'started'`
4. [ ] Attendre 2-3 minutes pour le premier cycle complet
5. [ ] Verify les données en production : `SELECT COUNT(*) FROM PRODUCTION.ORDERS`

### Post-déploiement

- [ ] Configurer les alertes (tasks en erreur, latence excessive)
- [ ] Create un dashboard de monitoring
- [ ] Planifier le nettoyage des données anciennes (RAW > 30 jours)
- [ ] Documenter les SLA pour l'équipe

---

## 🚨 Métriques de monitoring critiques

| Métrique | Threshold | Action si dépassé |
|----------|-----------|-------------------|
| **Latence pipeline** | < 5 minutes | Investiguer les tasks lentes |
| **Task failures** | 0% | Analyser les logs d'erreur |
| **Stream lag** | < 1000 events | Augmenter la fréquence des tasks |
| **Warehouse utilisation** | < 80% | Optimiser les requêtes ou scale up |
| **Stock alerts** | < 50 unités | Notifier l'équipe procurement |

---

**🍷 Architecture conçue pour la performance et la fiabilité !**
