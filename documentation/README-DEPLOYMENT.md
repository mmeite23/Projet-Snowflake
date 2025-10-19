# 🍷 Les Caves d'Albert - Guide de Déploiement Complet

## 📋 Architecture du Pipeline

```
┌─────────────────┐
│  Kafka Producer │ (Docker)
│   Wine Shop     │
└────────┬────────┘
         │ Kafka Topics
         ▼
┌─────────────────┐
│  Kafka Consumer │ (Docker)
│   → Snowflake   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│              SNOWFLAKE - CAVES_ALBERT_DB                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  📥 RAW LAYER (Bronze)                                  │
│  └─ RAW_DATA.RAW_EVENTS_STREAM                         │
│     ├─ EVENT_TYPE (VARCHAR)                            │
│     ├─ PRODUCT_ID (INTEGER)                            │
│     ├─ CUSTOMER_ID (INTEGER)                           │
│     ├─ EVENT_METADATA (OBJECT)                         │
│     └─ EVENT_CONTENT (VARIANT - JSON complet)          │
│                                                         │
│         ▼ STREAM_RAW_EVENTS (CDC)                      │
│         ▼ TASK_RAW_TO_STAGING_DISTRIBUTOR (1 min)      │
│                                                         │
│  🔄 STAGING LAYER (Silver)                              │
│  ├─ STAGING.STG_ORDERS                                 │
│  │  └─ Commandes transformées                          │
│  └─ STAGING.STG_INVENTORY_ADJUSTMENTS                  │
│     └─ Ajustements d'inventaire transformés            │
│                                                         │
│         ▼ STREAM_STG_ORDERS (CDC)                      │
│         ▼ STREAM_STG_INVENTORY_FOR_HISTORY (CDC)       │
│         ▼ STREAM_STG_INVENTORY_FOR_CURRENT (CDC)       │
│         ▼ 3 TASKS automatisées                         │
│                                                         │
│  ✨ PRODUCTION LAYER (Gold)                             │
│  ├─ PRODUCTION.ORDERS                                  │
│  │  └─ Commandes finales (MERGE - pas de doublons)    │
│  ├─ PRODUCTION.INVENTORY_HISTORY                       │
│  │  └─ Historique complet des mouvements              │
│  └─ PRODUCTION.INVENTORY_CURRENT                       │
│     └─ État actuel de l'inventaire par produit        │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Déploiement - Étape par Étape

### **Prérequis**

✅ Docker Desktop installé et en cours d'exécution  
✅ Compte Snowflake actif (CAVES_ALBERT_DB créée)  
✅ Warehouse COMPUTE_WH disponible  
✅ Python 3.9+ avec environnement `etl-snowflake`

---

### **1️⃣ Démarrer l'infrastructure Kafka**

```bash
cd /Users/mory_jr/Projet-Snowflake

# Démarrer tous les conteneurs Docker
docker-compose up -d

# Vérifier que tout tourne
docker ps

# Vous devriez voir :
# - redpanda (broker Kafka)
# - producer (génère des événements wine shop)
# - consumer (insère dans Snowflake)
```

**Logs du consumer (pour vérifier)** :
```bash
docker logs consumer --tail 50 --follow
```

Vous devriez voir :
```
✅ Batch committed successfully!
📈 Session stats - Orders: XXXX, Inventory: XXXX, Errors: 0
```

---

### **2️⃣ Vérifier que RAW_EVENTS_STREAM reçoit des données**

Dans Snowflake, exécutez :

```sql
USE DATABASE CAVES_ALBERT_DB;
USE SCHEMA RAW_DATA;

-- Compter les événements
SELECT COUNT(*) AS TOTAL_EVENTS FROM RAW_EVENTS_STREAM;

-- Voir un échantillon
SELECT 
    EVENT_TYPE,
    PRODUCT_ID,
    CUSTOMER_ID,
    EVENT_CONTENT,
    INGESTION_TIME
FROM RAW_EVENTS_STREAM
LIMIT 10;

-- Distribution par type d'événement
SELECT 
    EVENT_TYPE,
    COUNT(*) AS COUNT
FROM RAW_EVENTS_STREAM
GROUP BY EVENT_TYPE;
```

**Résultat attendu** :
```
EVENT_TYPE          | COUNT
--------------------|-------
ORDER_CREATED       | ~70%
INVENTORY_ADJUSTED  | ~30%
```

---

### **3️⃣ Déployer le pipeline Snowflake (Tasks & Streams)**

**Ouvrez Snowflake Worksheet** et exécutez **TOUT LE CONTENU** de :
```
snowflake-tasks-streams-CORRECTED.sql
```

Ce script va :
1. ✅ Créer les schémas STAGING et PRODUCTION
2. ✅ Créer 5 tables (2 staging + 3 production)
3. ✅ Créer 4 streams CDC
4. ✅ Créer 4 tasks automatisées
5. ✅ Activer les tasks

**Temps d'exécution** : ~30 secondes

---

### **4️⃣ Vérifier que les tasks sont actives**

```sql
-- Vérifier l'état des tasks
SHOW TASKS IN DATABASE CAVES_ALBERT_DB;

-- Vous devriez voir 4 tasks avec state = 'started'
```

**Output attendu** :
```
NAME                                    | STATE   | SCHEDULE
----------------------------------------|---------|----------
TASK_RAW_TO_STAGING_DISTRIBUTOR        | started | 1 MINUTE
TASK_STAGING_TO_PROD_ORDERS            | started | (child)
TASK_STAGING_TO_PROD_INVENTORY_HISTORY | started | (child)
TASK_STAGING_TO_PROD_INVENTORY_CURRENT | started | (child)
```

---

### **5️⃣ Attendre 2-3 minutes et vérifier la propagation des données**

```sql
-- Vue d'ensemble complète
SELECT 'RAW' AS LAYER, 'RAW_EVENTS_STREAM' AS TABLE_NAME, COUNT(*) AS ROWS 
FROM RAW_DATA.RAW_EVENTS_STREAM
UNION ALL
SELECT 'STAGING', 'STG_ORDERS', COUNT(*) FROM STAGING.STG_ORDERS
UNION ALL
SELECT 'STAGING', 'STG_INVENTORY_ADJUSTMENTS', COUNT(*) FROM STAGING.STG_INVENTORY_ADJUSTMENTS
UNION ALL
SELECT 'PRODUCTION', 'ORDERS', COUNT(*) FROM PRODUCTION.ORDERS
UNION ALL
SELECT 'PRODUCTION', 'INVENTORY_HISTORY', COUNT(*) FROM PRODUCTION.INVENTORY_HISTORY
UNION ALL
SELECT 'PRODUCTION', 'INVENTORY_CURRENT', COUNT(*) FROM PRODUCTION.INVENTORY_CURRENT
ORDER BY LAYER, TABLE_NAME;
```

**Résultat attendu** :
```
LAYER      | TABLE_NAME                  | ROWS
-----------|-----------------------------|---------
RAW        | RAW_EVENTS_STREAM           | ~10,000+
STAGING    | STG_ORDERS                  | ~7,000+
STAGING    | STG_INVENTORY_ADJUSTMENTS   | ~3,000+
PRODUCTION | ORDERS                      | ~7,000+
PRODUCTION | INVENTORY_HISTORY           | ~3,000+
PRODUCTION | INVENTORY_CURRENT           | ~500-1000
```

Si les tables STAGING et PRODUCTION sont encore vides :
- Attendre 1-2 minutes de plus (les tasks s'exécutent toutes les 1 minute)
- Ou exécuter manuellement : `EXECUTE TASK TASK_RAW_TO_STAGING_DISTRIBUTOR;`

---

### **6️⃣ Tester les requêtes analytiques**

```sql
-- 🍷 Top 10 des vins les plus vendus
SELECT
    PRODUCT_NAME,
    PRODUCT_CATEGORY,
    COUNT(*) AS ORDER_COUNT,
    SUM(QUANTITY) AS TOTAL_QUANTITY,
    ROUND(SUM(TOTAL_AMOUNT), 2) AS TOTAL_REVENUE
FROM PRODUCTION.ORDERS
GROUP BY PRODUCT_NAME, PRODUCT_CATEGORY
ORDER BY TOTAL_REVENUE DESC
LIMIT 10;

-- 📊 État actuel de l'inventaire par catégorie
SELECT
    PRODUCT_CATEGORY,
    COUNT(DISTINCT PRODUCT_ID) AS PRODUCT_COUNT,
    SUM(CURRENT_STOCK_LEVEL) AS TOTAL_STOCK,
    ROUND(AVG(CURRENT_STOCK_LEVEL), 0) AS AVG_STOCK_PER_PRODUCT
FROM PRODUCTION.INVENTORY_CURRENT
GROUP BY PRODUCT_CATEGORY
ORDER BY TOTAL_STOCK DESC;

-- 📈 Chiffre d'affaires par jour (derniers 7 jours)
SELECT
    ORDER_DATE,
    COUNT(*) AS ORDER_COUNT,
    ROUND(SUM(TOTAL_AMOUNT), 2) AS DAILY_REVENUE
FROM PRODUCTION.ORDERS
WHERE ORDER_DATE >= DATEADD('day', -7, CURRENT_DATE())
GROUP BY ORDER_DATE
ORDER BY ORDER_DATE DESC;
```

---

## 🔍 Monitoring et Dépannage

### **Vérifier l'historique des tasks**

```sql
SELECT
    NAME AS TASK_NAME,
    STATE,
    SCHEDULED_TIME,
    COMPLETED_TIME,
    DATEDIFF('second', SCHEDULED_TIME, COMPLETED_TIME) AS DURATION_SECONDS,
    ERROR_CODE,
    ERROR_MESSAGE
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(
    SCHEDULED_TIME_RANGE_START => DATEADD('hour', -1, CURRENT_TIMESTAMP())
))
WHERE NAME LIKE 'TASK_%'
ORDER BY SCHEDULED_TIME DESC
LIMIT 20;
```

### **Vérifier les streams**

```sql
-- Voir si des données sont en attente dans les streams
SELECT 'STREAM_RAW_EVENTS' AS STREAM_NAME, 
       SYSTEM$STREAM_HAS_DATA('STREAM_RAW_EVENTS') AS HAS_DATA,
       (SELECT COUNT(*) FROM STREAM_RAW_EVENTS) AS PENDING_ROWS
UNION ALL
SELECT 'STREAM_STG_ORDERS', 
       SYSTEM$STREAM_HAS_DATA('STREAM_STG_ORDERS'),
       (SELECT COUNT(*) FROM STREAM_STG_ORDERS);
```

### **Vérifier les logs Docker**

```bash
# Consumer Kafka → Snowflake
docker logs consumer --tail 100 --follow

# Producer (génère les événements)
docker logs producer --tail 50

# RedPanda (broker Kafka)
docker logs redpanda --tail 50
```

---

## ⚠️ Problèmes Courants et Solutions

### **❌ Problème : Les tables STAGING/PRODUCTION sont vides**

**Causes possibles** :
1. Les tasks ne sont pas actives → Exécutez `SHOW TASKS;` et vérifiez `state = 'started'`
2. Les streams sont vides → Exécutez `SELECT COUNT(*) FROM STREAM_RAW_EVENTS;`
3. La condition `WHEN SYSTEM$STREAM_HAS_DATA(...)` retourne FALSE

**Solution rapide** :
```sql
-- Exécuter manuellement les tasks
EXECUTE TASK TASK_RAW_TO_STAGING_DISTRIBUTOR;

-- Attendre 5 secondes
SELECT SYSTEM$WAIT(5, 'SECONDS');

-- Vérifier STAGING
SELECT COUNT(*) FROM STAGING.STG_ORDERS;
```

---

### **❌ Problème : Consumer Docker affiche des erreurs**

**Erreur** : `Table 'RAW_EVENTS_STREAM' does not exist`

**Solution** :
```bash
# Redémarrer le consumer pour qu'il recrée la table
docker restart consumer

# Attendre 10 secondes
sleep 10

# Vérifier les logs
docker logs consumer --tail 30
```

---

### **❌ Problème : Warehouse suspendu**

**Erreur dans TASK_HISTORY** : `Warehouse 'COMPUTE_WH' not available`

**Solution** :
```sql
-- Activer le warehouse
ALTER WAREHOUSE COMPUTE_WH RESUME;

-- Vérifier qu'il tourne
SHOW WAREHOUSES LIKE 'COMPUTE_WH';
```

---

## 📊 Métriques de Performance

### **Débit attendu** :

| Composant | Métrique | Valeur |
|-----------|----------|--------|
| Producer | Événements/sec | ~100-200 |
| Consumer | Batch size | ~100-2500 événements |
| Consumer | Latence | ~2-3 secondes/batch |
| Tasks Snowflake | Fréquence | Toutes les 1 minute |
| Tasks Snowflake | Durée | ~2-5 secondes |

---

## 📁 Fichiers du Projet

```
Projet-Snowflake/
├── docker-compose.yml                          # Infrastructure Kafka
├── streaming/
│   ├── kafka_producer.py                       # Génère les événements
│   └── kafka_consumer_snowflake.py             # Ingestion Snowflake
├── snowflake-tasks-streams-CORRECTED.sql       # 🎯 Script principal
├── fix-recreate-raw-table.sql                  # Utilitaire de réparation
├── execute-tasks-now.sql                       # Exécution manuelle
├── SNOWFLAKE_AUTOMATION_GUIDE.md               # Documentation détaillée
└── README-DEPLOYMENT.md                        # 📖 Ce fichier
```

---

## ✅ Checklist Finale

- [ ] Docker Desktop en cours d'exécution
- [ ] Producer, Consumer, RedPanda actifs (`docker ps`)
- [ ] Consumer insère dans Snowflake sans erreurs (`docker logs consumer`)
- [ ] RAW_EVENTS_STREAM contient des données (`SELECT COUNT(*)...`)
- [ ] Script `snowflake-tasks-streams-CORRECTED.sql` exécuté avec succès
- [ ] 4 tasks actives (`SHOW TASKS;` → state = 'started')
- [ ] STAGING et PRODUCTION remplis après 2-3 minutes
- [ ] Requêtes analytiques retournent des résultats

---

## 🎯 Prochaines Étapes (Optionnel)

### **A. Créer un Dashboard Snowflake**

Créez des vues matérialisées pour des requêtes plus rapides :

```sql
CREATE OR REPLACE VIEW ANALYTICS.DAILY_SALES AS
SELECT
    ORDER_DATE,
    COUNT(*) AS ORDER_COUNT,
    SUM(TOTAL_AMOUNT) AS DAILY_REVENUE,
    AVG(TOTAL_AMOUNT) AS AVG_ORDER_VALUE
FROM PRODUCTION.ORDERS
GROUP BY ORDER_DATE;
```

### **B. Ajouter des alertes**

```sql
-- Alerte : Stock critique (< 10 unités)
SELECT 
    PRODUCT_NAME,
    CURRENT_STOCK_LEVEL,
    WAREHOUSE_LOCATION
FROM PRODUCTION.INVENTORY_CURRENT
WHERE CURRENT_STOCK_LEVEL < 10
ORDER BY CURRENT_STOCK_LEVEL ASC;
```

### **C. Exporter vers Tableau/PowerBI**

Connectez Tableau Desktop à Snowflake :
- Host : `<your-account>.snowflakecomputing.com`
- Database : `CAVES_ALBERT_DB`
- Schema : `PRODUCTION`
- Tables : `ORDERS`, `INVENTORY_CURRENT`

---

## 📞 Support

Si vous rencontrez des problèmes :
1. Vérifiez les logs : `docker logs consumer --tail 100`
2. Vérifiez l'historique des tasks : `SELECT * FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY(...))`
3. Consultez `SNOWFLAKE_AUTOMATION_GUIDE.md` pour plus de détails

---

**🍷 Bon déploiement avec Les Caves d'Albert ! 🍷**
