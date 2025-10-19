# ⚡ Quick Start - Les Caves d'Albert Pipeline

## 🎯 En 3 étapes

### **1️⃣ Vérifier que les données arrivent (30 secondes)**

```sql
USE DATABASE CAVES_ALBERT_DB;
USE SCHEMA RAW_DATA;

SELECT COUNT(*) AS TOTAL_EVENTS FROM RAW_EVENTS_STREAM;
-- Attendu: > 1000
```

### **2️⃣ Déployer le pipeline (2 minutes)**

Dans Snowflake, exécutez **TOUT** le fichier :
```
snowflake-tasks-streams-CORRECTED.sql
```

✅ Créé : 5 tables + 4 streams + 4 tasks

### **3️⃣ Vérifier que ça marche (3 minutes d'attente)**

```sql
-- Attendez 2-3 minutes puis :
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
SELECT 'PRODUCTION', 'INVENTORY_CURRENT', COUNT(*) FROM PRODUCTION.INVENTORY_CURRENT;
```

**Si tout fonctionne** :
```
LAYER      | TABLE_NAME                | ROWS
-----------|---------------------------|--------
RAW        | RAW_EVENTS_STREAM        | 10,000+
STAGING    | STG_ORDERS               |  7,000+
STAGING    | STG_INVENTORY_ADJUSTMENTS|  3,000+
PRODUCTION | ORDERS                   |  7,000+
PRODUCTION | INVENTORY_HISTORY        |  3,000+
PRODUCTION | INVENTORY_CURRENT        |    500+
```

---

## 🔧 Si STAGING/PRODUCTION sont vides

```sql
-- Option A : Exécution manuelle (résultat immédiat)
EXECUTE TASK TASK_RAW_TO_STAGING_DISTRIBUTOR;

-- Attendre 10 secondes
SELECT SYSTEM$WAIT(10, 'SECONDS');

-- Vérifier
SELECT COUNT(*) FROM STAGING.STG_ORDERS;
SELECT COUNT(*) FROM PRODUCTION.ORDERS;
```

**Option B : Attendre 2 minutes** (les tasks s'exécutent automatiquement toutes les 1 minute)

---

## 📊 Première requête analytique

```sql
-- 🍷 Top 5 des vins les plus vendus
SELECT
    PRODUCT_NAME,
    PRODUCT_CATEGORY,
    COUNT(*) AS ORDER_COUNT,
    ROUND(SUM(TOTAL_AMOUNT), 2) AS TOTAL_REVENUE
FROM PRODUCTION.ORDERS
GROUP BY PRODUCT_NAME, PRODUCT_CATEGORY
ORDER BY TOTAL_REVENUE DESC
LIMIT 5;
```

---

## ✅ Checklist Rapide

- [ ] Consumer Docker actif : `docker logs consumer --tail 20`
- [ ] RAW_EVENTS_STREAM a des données : `SELECT COUNT(*) ...`
- [ ] Script SQL exécuté sans erreurs
- [ ] Tasks actives : `SHOW TASKS;` (state = 'started')
- [ ] STAGING rempli après 2 min
- [ ] PRODUCTION rempli après 3 min

---

**🚀 Prêt ! Consultez `README-DEPLOYMENT.md` pour plus de détails.**
