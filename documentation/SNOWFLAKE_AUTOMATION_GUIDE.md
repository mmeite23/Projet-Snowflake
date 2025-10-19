# 🍷 Les Caves d'Albert - Guide d'Automatisation Snowflake

## 📋 Table des Matières
1. [Vue d'ensemble](#vue-densemble)
2. [Architecture des Tasks et Streams](#architecture-des-tasks-et-streams)
3. [Schémas de données](#schémas-de-données)
4. [Guide d'implémentation](#guide-dimplémentation)
5. [Monitoring et maintenance](#monitoring-et-maintenance)
6. [Cas d'usage analytiques](#cas-dusage-analytiques)

---

## 🎯 Vue d'ensemble

### Architecture en 3 couches

```
┌─────────────────────────────────────────────────────────────┐
│  KAFKA PRODUCER → REDPANDA → CONSUMER → SNOWFLAKE          │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: RAW (Bronze)                                      │
│  └── RAW_EVENTS_STREAM (données brutes JSON)                │
└─────────────────────────────────────────────────────────────┘
                              ↓ STREAMS + TASKS
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: STAGING (Silver)                                  │
│  ├── STG_ORDERS (commandes transformées)                    │
│  └── STG_INVENTORY_ADJUSTMENTS (ajustements transformés)    │
└─────────────────────────────────────────────────────────────┘
                              ↓ STREAMS + TASKS
┌─────────────────────────────────────────────────────────────┐
│  LAYER 3: PRODUCTION (Gold)                                 │
│  ├── ORDERS (commandes finales)                             │
│  ├── INVENTORY_CURRENT (inventaire temps réel)              │
│  └── INVENTORY_HISTORY (historique complet)                 │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Architecture des Tasks et Streams

### DAG (Directed Acyclic Graph) des Tasks

```
┌──────────────────────────────────────────────┐
│  TASK_RAW_TO_STAGING_ORDERS                  │
│  ⏱️  Schedule: 1 MINUTE                      │
│  📊 Source: STREAM_RAW_ORDERS                │
│  🎯 Target: STAGING.STG_ORDERS               │
└──────────────────┬───────────────────────────┘
                   │
                   ↓
┌──────────────────────────────────────────────┐
│  TASK_STAGING_TO_PROD_ORDERS                 │
│  🔗 Trigger: AFTER parent task               │
│  📊 Source: STREAM_STG_ORDERS                │
│  🎯 Target: PRODUCTION.ORDERS                │
└──────────────────────────────────────────────┘


┌──────────────────────────────────────────────┐
│  TASK_RAW_TO_STAGING_INVENTORY               │
│  ⏱️  Schedule: 1 MINUTE                      │
│  📊 Source: STREAM_RAW_INVENTORY             │
│  🎯 Target: STAGING.STG_INVENTORY_ADJ        │
└──────────────────┬───────────────────────────┘
                   │
                   ↓
┌──────────────────────────────────────────────┐
│  TASK_STAGING_TO_PROD_INVENTORY_HISTORY      │
│  🔗 Trigger: AFTER parent task               │
│  📊 Source: STREAM_STG_INVENTORY             │
│  🎯 Target: PRODUCTION.INVENTORY_HISTORY     │
└──────────────────┬───────────────────────────┘
                   │
                   ↓
┌──────────────────────────────────────────────┐
│  TASK_STAGING_TO_PROD_INVENTORY_CURRENT      │
│  🔗 Trigger: AFTER parent task               │
│  📊 Source: STREAM_STG_INVENTORY             │
│  🎯 Target: PRODUCTION.INVENTORY_CURRENT     │
└──────────────────────────────────────────────┘
```

### Types de Streams

| Stream | Table Source | Mode | Description |
|--------|-------------|------|-------------|
| `STREAM_RAW_ORDERS` | `RAW_EVENTS_STREAM` | APPEND_ONLY | Capture uniquement les nouveaux événements ORDER_CREATED |
| `STREAM_RAW_INVENTORY` | `RAW_EVENTS_STREAM` | APPEND_ONLY | Capture uniquement les nouveaux événements INVENTORY_ADJUSTED |
| `STREAM_STG_ORDERS` | `STAGING.STG_ORDERS` | STANDARD | Capture INSERT/UPDATE/DELETE pour CDC complet |
| `STREAM_STG_INVENTORY` | `STAGING.STG_INVENTORY_ADJ` | STANDARD | Capture INSERT/UPDATE/DELETE pour CDC complet |

---

## 📊 Schémas de données

### RAW Layer (Bronze)

```sql
RAW_EVENTS_STREAM
├── EVENT_ID (VARCHAR) - UUID unique
├── EVENT_TYPE (VARCHAR) - 'ORDER_CREATED' ou 'INVENTORY_ADJUSTED'
├── EVENT_TIMESTAMP (TIMESTAMP_NTZ) - Timestamp de l'événement
├── PRODUCT_ID (VARCHAR) - ID produit (ex: PROD-001)
├── CUSTOMER_ID (VARCHAR) - ID client (ex: CUST-12345)
├── EVENT_DATA (VARIANT) - JSON contenant toutes les données
└── INGESTION_TIMESTAMP (TIMESTAMP_NTZ) - Timestamp d'ingestion Kafka
```

**Exemple EVENT_DATA pour ORDER_CREATED:**
```json
{
  "order_id": "ORD-20251019-123456",
  "customer_id": "CUST-67890",
  "product_name": "🍷 Château Margaux 2015",
  "product_category": "Rouge",
  "quantity": 2,
  "unit_price": 450.00,
  "total_amount": 900.00,
  "payment_method": "CARTE_BANCAIRE",
  "shipping_address": "123 Rue de la Paix, 75002 Paris"
}
```

**Exemple EVENT_DATA pour INVENTORY_ADJUSTED:**
```json
{
  "adjustment_id": "ADJ-20251019-789012",
  "product_name": "🥂 Moët & Chandon Brut Imperial",
  "product_category": "Effervescent",
  "adjustment_type": "RESTOCK",
  "quantity_change": 50,
  "new_stock_level": 250,
  "reason": "Réapprovisionnement hebdomadaire",
  "warehouse_location": "Entrepôt Paris Nord"
}
```

### STAGING Layer (Silver)

Tables intermédiaires avec données extraites du JSON et nettoyées.

**STG_ORDERS** - Commandes prêtes pour la production
**STG_INVENTORY_ADJUSTMENTS** - Ajustements d'inventaire prêts pour la production

### PRODUCTION Layer (Gold)

Tables finales optimisées pour l'analytique.

**ORDERS** - Toutes les commandes clients (MERGE avec UPDATE si même ORDER_ID)
**INVENTORY_CURRENT** - État actuel de l'inventaire par produit (1 ligne par produit)
**INVENTORY_HISTORY** - Historique complet de tous les ajustements (audit trail)

---

## 🚀 Guide d'implémentation

### Étape 1: Préparer les schémas

```sql
-- Créer les schémas si nécessaire
CREATE SCHEMA IF NOT EXISTS STAGING;
CREATE SCHEMA IF NOT EXISTS PRODUCTION;

-- Vérifier
SHOW SCHEMAS IN DATABASE CAVES_ALBERT_DB;
```

### Étape 2: Exécuter le script principal

```sql
-- Exécuter snowflake-tasks-streams.sql dans Snowflake
-- Cela créera :
-- ✅ 5 tables (2 staging + 3 production)
-- ✅ 4 streams (CDC)
-- ✅ 5 tasks (pipelines automatisés)
```

### Étape 3: Activer les tasks

```sql
-- Les tasks sont activées automatiquement dans le script
-- Vérifier l'état :
SHOW TASKS IN SCHEMA RAW_DATA;

-- Résultat attendu :
-- STATE = 'started' pour toutes les tasks
```

### Étape 4: Vérifier le flux de données

```sql
-- 1. Vérifier les streams
SELECT 'STREAM_RAW_ORDERS' AS STREAM, 
       SYSTEM$STREAM_HAS_DATA('STREAM_RAW_ORDERS') AS HAS_DATA,
       (SELECT COUNT(*) FROM STREAM_RAW_ORDERS) AS ROW_COUNT;

-- 2. Voir les données qui transitent
SELECT * FROM STREAM_RAW_ORDERS LIMIT 10;

-- 3. Vérifier l'historique des tasks
SELECT
    NAME,
    STATE,
    SCHEDULED_TIME,
    COMPLETED_TIME,
    DATEDIFF('second', SCHEDULED_TIME, COMPLETED_TIME) AS DURATION_SEC
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY())
WHERE NAME LIKE 'TASK_%'
ORDER BY SCHEDULED_TIME DESC
LIMIT 10;
```

---

## 📈 Monitoring et maintenance

### Dashboard de monitoring

```sql
-- Vue d'ensemble du pipeline
CREATE OR REPLACE VIEW MONITORING.PIPELINE_HEALTH AS
SELECT
    'RAW_EVENTS_STREAM' AS TABLE_NAME,
    COUNT(*) AS ROW_COUNT,
    MAX(INGESTION_TIMESTAMP) AS LAST_INGESTION
FROM RAW_EVENTS_STREAM
UNION ALL
SELECT
    'STG_ORDERS',
    COUNT(*),
    MAX(INGESTION_TIMESTAMP)
FROM STAGING.STG_ORDERS
UNION ALL
SELECT
    'STG_INVENTORY_ADJUSTMENTS',
    COUNT(*),
    MAX(INGESTION_TIMESTAMP)
FROM STAGING.STG_INVENTORY_ADJUSTMENTS
UNION ALL
SELECT
    'ORDERS',
    COUNT(*),
    MAX(UPDATED_AT)
FROM PRODUCTION.ORDERS
UNION ALL
SELECT
    'INVENTORY_CURRENT',
    COUNT(*),
    MAX(UPDATED_AT)
FROM PRODUCTION.INVENTORY_CURRENT
UNION ALL
SELECT
    'INVENTORY_HISTORY',
    COUNT(*),
    MAX(CREATED_AT)
FROM PRODUCTION.INVENTORY_HISTORY;
```

### Alertes importantes

```sql
-- 1. Tasks en erreur
SELECT
    NAME,
    STATE,
    ERROR_CODE,
    ERROR_MESSAGE,
    SCHEDULED_TIME
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY())
WHERE STATE = 'FAILED'
    AND SCHEDULED_TIME > DATEADD('hour', -1, CURRENT_TIMESTAMP())
ORDER BY SCHEDULED_TIME DESC;

-- 2. Latence du pipeline (plus de 5 minutes)
SELECT
    MAX(INGESTION_TIMESTAMP) AS LAST_RAW_INGESTION,
    MAX(UPDATED_AT) AS LAST_PROD_UPDATE,
    DATEDIFF('minute', MAX(UPDATED_AT), CURRENT_TIMESTAMP()) AS LATENCY_MINUTES
FROM PRODUCTION.ORDERS;

-- 3. Produits en rupture de stock
SELECT
    PRODUCT_ID,
    PRODUCT_NAME,
    PRODUCT_CATEGORY,
    CURRENT_STOCK_LEVEL,
    LAST_ADJUSTMENT_TIMESTAMP
FROM PRODUCTION.INVENTORY_CURRENT
WHERE CURRENT_STOCK_LEVEL <= 0
ORDER BY LAST_ADJUSTMENT_TIMESTAMP DESC;
```

### Maintenance régulière

```sql
-- 1. Nettoyer les anciennes données RAW (> 30 jours)
DELETE FROM RAW_EVENTS_STREAM
WHERE INGESTION_TIMESTAMP < DATEADD('day', -30, CURRENT_TIMESTAMP());

-- 2. Nettoyer les données STAGING (> 7 jours)
DELETE FROM STAGING.STG_ORDERS
WHERE INGESTION_TIMESTAMP < DATEADD('day', -7, CURRENT_TIMESTAMP());

DELETE FROM STAGING.STG_INVENTORY_ADJUSTMENTS
WHERE INGESTION_TIMESTAMP < DATEADD('day', -7, CURRENT_TIMESTAMP());

-- 3. Archiver l'historique ancien (> 1 an) dans une table d'archive
CREATE TABLE IF NOT EXISTS PRODUCTION.INVENTORY_HISTORY_ARCHIVE 
    LIKE PRODUCTION.INVENTORY_HISTORY;

INSERT INTO PRODUCTION.INVENTORY_HISTORY_ARCHIVE
SELECT * FROM PRODUCTION.INVENTORY_HISTORY
WHERE ADJUSTMENT_DATE < DATEADD('year', -1, CURRENT_DATE());

DELETE FROM PRODUCTION.INVENTORY_HISTORY
WHERE ADJUSTMENT_DATE < DATEADD('year', -1, CURRENT_DATE());
```

---

## 📊 Cas d'usage analytiques

### 1. Dashboard KPI temps réel

```sql
-- Métriques clés du jour
SELECT
    COUNT(*) AS ORDERS_TODAY,
    SUM(TOTAL_AMOUNT) AS REVENUE_TODAY,
    AVG(TOTAL_AMOUNT) AS AVG_ORDER_VALUE,
    COUNT(DISTINCT CUSTOMER_ID) AS UNIQUE_CUSTOMERS
FROM PRODUCTION.ORDERS
WHERE ORDER_DATE = CURRENT_DATE();
```

### 2. Analyse des ventes par catégorie

```sql
SELECT
    PRODUCT_CATEGORY,
    COUNT(*) AS ORDER_COUNT,
    SUM(QUANTITY) AS UNITS_SOLD,
    SUM(TOTAL_AMOUNT) AS TOTAL_REVENUE,
    AVG(UNIT_PRICE) AS AVG_PRICE
FROM PRODUCTION.ORDERS
WHERE ORDER_DATE >= DATEADD('day', -30, CURRENT_DATE())
GROUP BY PRODUCT_CATEGORY
ORDER BY TOTAL_REVENUE DESC;
```

### 3. Top clients (fidélité)

```sql
SELECT
    CUSTOMER_ID,
    COUNT(*) AS ORDER_COUNT,
    SUM(TOTAL_AMOUNT) AS LIFETIME_VALUE,
    AVG(TOTAL_AMOUNT) AS AVG_ORDER_VALUE,
    MAX(ORDER_DATE) AS LAST_ORDER_DATE,
    DATEDIFF('day', MAX(ORDER_DATE), CURRENT_DATE()) AS DAYS_SINCE_LAST_ORDER
FROM PRODUCTION.ORDERS
GROUP BY CUSTOMER_ID
HAVING ORDER_COUNT >= 5
ORDER BY LIFETIME_VALUE DESC
LIMIT 20;
```

### 4. Prévision de rupture de stock

```sql
-- Calculer le taux de vente moyen et estimer les jours de stock restants
WITH daily_sales AS (
    SELECT
        PRODUCT_ID,
        PRODUCT_NAME,
        PRODUCT_CATEGORY,
        AVG(daily_quantity) AS AVG_DAILY_SALES
    FROM (
        SELECT
            PRODUCT_ID,
            PRODUCT_NAME,
            PRODUCT_CATEGORY,
            ORDER_DATE,
            SUM(QUANTITY) AS daily_quantity
        FROM PRODUCTION.ORDERS
        WHERE ORDER_DATE >= DATEADD('day', -30, CURRENT_DATE())
        GROUP BY PRODUCT_ID, PRODUCT_NAME, PRODUCT_CATEGORY, ORDER_DATE
    )
    GROUP BY PRODUCT_ID, PRODUCT_NAME, PRODUCT_CATEGORY
)
SELECT
    i.PRODUCT_ID,
    i.PRODUCT_NAME,
    i.PRODUCT_CATEGORY,
    i.CURRENT_STOCK_LEVEL,
    s.AVG_DAILY_SALES,
    CASE
        WHEN s.AVG_DAILY_SALES > 0 THEN
            ROUND(i.CURRENT_STOCK_LEVEL / s.AVG_DAILY_SALES, 1)
        ELSE NULL
    END AS DAYS_OF_STOCK_REMAINING,
    CASE
        WHEN i.CURRENT_STOCK_LEVEL / s.AVG_DAILY_SALES < 7 THEN '🔴 URGENT'
        WHEN i.CURRENT_STOCK_LEVEL / s.AVG_DAILY_SALES < 14 THEN '🟠 ATTENTION'
        ELSE '🟢 OK'
    END AS STOCK_STATUS
FROM PRODUCTION.INVENTORY_CURRENT i
JOIN daily_sales s ON i.PRODUCT_ID = s.PRODUCT_ID
WHERE s.AVG_DAILY_SALES > 0
ORDER BY DAYS_OF_STOCK_REMAINING ASC;
```

### 5. Analyse de la saisonnalité

```sql
SELECT
    DAYNAME(ORDER_DATE) AS DAY_OF_WEEK,
    HOUR(ORDER_TIMESTAMP) AS HOUR_OF_DAY,
    COUNT(*) AS ORDER_COUNT,
    SUM(TOTAL_AMOUNT) AS REVENUE
FROM PRODUCTION.ORDERS
WHERE ORDER_DATE >= DATEADD('day', -90, CURRENT_DATE())
GROUP BY DAYNAME(ORDER_DATE), HOUR(ORDER_TIMESTAMP)
ORDER BY ORDER_COUNT DESC;
```

---

## 🎯 Avantages de cette architecture

### ✅ Temps réel
- Les tasks s'exécutent toutes les 1 minute
- Latence totale < 2-3 minutes de bout en bout
- Données disponibles pour l'analytique quasi instantanément

### ✅ Coût optimisé
- Les tasks ne s'exécutent que si des données sont présentes (`WHEN SYSTEM$STREAM_HAS_DATA()`)
- Pas de traitement inutile = pas de crédits Snowflake gaspillés
- Warehouse se suspend automatiquement entre les exécutions

### ✅ Fiabilité
- CDC (Change Data Capture) natif avec les streams
- Garantie de traitement exactement une fois (exactly-once)
- Traçabilité complète avec les timestamps d'ingestion

### ✅ Scalabilité
- Architecture modulaire (RAW → STAGING → PROD)
- Facile d'ajouter de nouveaux types d'événements
- Support de millions d'événements par jour

### ✅ Maintenabilité
- SQL pur, pas de code externe
- Monitoring intégré avec `TASK_HISTORY()`
- Facile à débugger et à modifier

---

## 🔧 Dépannage

### Problème : Les tasks ne s'exécutent pas

```sql
-- 1. Vérifier que les tasks sont bien actives
SHOW TASKS;

-- 2. Activer manuellement si nécessaire
ALTER TASK TASK_RAW_TO_STAGING_ORDERS RESUME;

-- 3. Exécuter manuellement pour tester
EXECUTE TASK TASK_RAW_TO_STAGING_ORDERS;
```

### Problème : Les streams sont vides

```sql
-- Vérifier que des données arrivent dans RAW
SELECT COUNT(*) FROM RAW_EVENTS_STREAM
WHERE INGESTION_TIMESTAMP > DATEADD('minute', -5, CURRENT_TIMESTAMP());

-- Vérifier que le consumer Kafka fonctionne
-- (voir les logs Docker du container consumer)
```

### Problème : Erreurs dans les tasks

```sql
-- Voir les erreurs détaillées
SELECT
    NAME,
    ERROR_CODE,
    ERROR_MESSAGE,
    QUERY_TEXT
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY())
WHERE STATE = 'FAILED'
ORDER BY SCHEDULED_TIME DESC
LIMIT 5;
```

---

## 📚 Ressources

- [Snowflake Streams Documentation](https://docs.snowflake.com/en/user-guide/streams-intro)
- [Snowflake Tasks Documentation](https://docs.snowflake.com/en/user-guide/tasks-intro)
- [CDC with Streams](https://docs.snowflake.com/en/user-guide/streams-cdc)
- [Task DAGs](https://docs.snowflake.com/en/user-guide/tasks-intro#task-graphs)

---

**🍷 Bon traitement de données en temps réel avec Les Caves d'Albert !**
