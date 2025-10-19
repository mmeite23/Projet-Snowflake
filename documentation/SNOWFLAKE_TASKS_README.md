# 🍷 Les Caves d'Albert - Snowflake Tasks & Streams

## 📌 Vue d'ensemble

Ce dossier contient l'implémentation complète d'un **pipeline automatisé Snowflake** pour traiter les événements en temps réel de la plateforme "Les Caves d'Albert" (boutique de vins en ligne).

### Architecture complète

```
Kafka Producer → RedPanda → Consumer → Snowflake RAW → STAGING → PRODUCTION
                                          ↓         ↓         ↓
                                      Streams   Tasks    Analytics
```

---

## 📂 Fichiers disponibles

| Fichier | Description | Usage |
|---------|-------------|-------|
| **`snowflake-tasks-streams.sql`** | Script principal de déploiement | Create toutes les tables, streams et tasks |
| **`SNOWFLAKE_AUTOMATION_GUIDE.md`** | Guide complet d'implémentation | Documentation technique détaillée |
| **`ARCHITECTURE_DIAGRAM.md`** | Diagrammes et flux de données | Comprendre l'architecture visuelle |
| **`analytical-queries.sql`** | 50+ requêtes prêtes à l'emploi | Analyses business et dashboards |

---

## 🚀 Quick Start (5 minutes)

### Prerequisites

- ✅ Base de données `CAVES_ALBERT_DB` créée dans Snowflake
- ✅ Schémas `RAW_DATA`, `STAGING`, `PRODUCTION` créés
- ✅ Warehouse `COMPUTE_WH` disponible
- ✅ Consumer Kafka ingère des données dans `RAW_EVENTS_STREAM`

### Installation en 3 étapes

#### 1️⃣ Verify que des données arrivent

```sql
USE DATABASE CAVES_ALBERT_DB;
USE SCHEMA RAW_DATA;

SELECT COUNT(*) FROM RAW_EVENTS_STREAM;
-- Résultat attendu : > 0 événements
```

#### 2️⃣ Execute le script de déploiement

```sql
-- Copier/coller le contenu de snowflake-tasks-streams.sql
-- dans Snowflake et execute tout le script
```

#### 3️⃣ Verify l'activation

```sql
-- Verify que les tasks sont actives
SHOW TASKS IN SCHEMA RAW_DATA;
-- Résultat : STATE = 'started' pour toutes les tasks

-- Attendre 2-3 minutes et verify les données
SELECT COUNT(*) FROM PRODUCTION.ORDERS;
SELECT COUNT(*) FROM PRODUCTION.INVENTORY_CURRENT;
```

✅ **C'est tout !** Le pipeline est maintenant opérationnel.

---

## 📊 Architecture des données

### 🥉 Layer 1: RAW (Bronze)

**Table : `RAW_EVENTS_STREAM`**
- Données brutes ingérées depuis Kafka
- Format JSON dans `EVENT_DATA` (VARIANT)
- Conservation : 30 jours

### 🥈 Layer 2: STAGING (Silver)

**Tables :**
- `STG_ORDERS` - Commandes transformées (JSON → colonnes)
- `STG_INVENTORY_ADJUSTMENTS` - Ajustements d'inventaire transformés
- Conservation : 7 jours

### 🥇 Layer 3: PRODUCTION (Gold)

**Tables :**
- `ORDERS` - Toutes les commandes clients (table finale)
- `INVENTORY_CURRENT` - État actuel de l'inventaire (1 ligne/produit)
- `INVENTORY_HISTORY` - Historique complet des ajustements (audit trail)
- Conservation : Illimitée

---

## 🔄 Pipeline automatisé (Tasks & Streams)

### DAG des Tasks

```
TASK_RAW_TO_STAGING_ORDERS (1 min)
    └─→ TASK_STAGING_TO_PROD_ORDERS (trigger after parent)

TASK_RAW_TO_STAGING_INVENTORY (1 min)
    └─→ TASK_STAGING_TO_PROD_INVENTORY_HISTORY (trigger after parent)
        └─→ TASK_STAGING_TO_PROD_INVENTORY_CURRENT (trigger after parent)
```

### Caractéristiques

- ⚡ **Latence** : < 3 minutes de bout en bout
- 💰 **Coût optimisé** : Tasks s'exécutent uniquement si données présentes
- 🔒 **Fiabilité** : CDC natif avec Snowflake Streams
- 📊 **Traçabilité** : Timestamps à chaque étape

---

## 📈 Cas d'usage analytiques

Le fichier `analytical-queries.sql` contient **50+ requêtes** organisées en 10 sections :

### 1. 📊 KPI temps réel
- Dashboard du jour (commandes, revenus, clients)
- Comparaison aujourd'hui vs hier
- État de l'inventaire en temps réel

### 2. 🏆 Top performers
- Top 10 produits par revenus
- Top 10 produits par volume
- Top 20 clients par valeur
- Top catégories de produits

### 3. 📈 Tendances et évolution
- Évolution des ventes par jour/semaine/mois
- Analyse de saisonnalité (jour de la semaine, heures de pointe)
- Tendance par catégorie

### 4. 🔍 Analyse des clients
- Segmentation RFM (Recency, Frequency, Monetary)
- Clients fidèles (5+ commandes)
- Clients inactifs (30+ jours sans achat)

### 5. 📦 Gestion d'inventaire
- Alertes de stock bas (< 50 unités)
- Prévision de rupture de stock
- Historique des ajustements
- Rotation des stocks (turnover rate)

### 6. 💰 Analyse financière
- Revenus par mode de paiement
- Panier moyen par catégorie
- Évolution mensuelle (MoM)

### 7. 🎯 Performance produit
- Produits les plus rentables
- Analyse ABC (Pareto 80/20)
- Produits en déclin

### 8. 🔔 Alertes et monitoring
- Vue d'ensemble des alertes
- Rapport de santé du pipeline

### 9. 📊 Vues matérialisées
- `VW_DAILY_KPI` - KPI quotidiens
- `VW_PRODUCT_PERFORMANCE` - Performance par produit
- `VW_INVENTORY_ALERTS` - Inventaire avec alertes

### 10. 🎓 Exemples d'usage
- Dashboard manager
- Rapport hebdomadaire
- Liste de commandes à préparer

---

## 🎯 Exemples concrets

### Exemple 1 : Top 5 vins les plus vendus cette semaine

```sql
SELECT
    PRODUCT_NAME,
    SUM(QUANTITY) AS UNITS_SOLD,
    SUM(TOTAL_AMOUNT) AS REVENUE
FROM PRODUCTION.ORDERS
WHERE ORDER_DATE >= DATE_TRUNC('week', CURRENT_DATE())
GROUP BY PRODUCT_NAME
ORDER BY UNITS_SOLD DESC
LIMIT 5;
```

### Exemple 2 : Clients VIP (> 1000€ de commandes)

```sql
SELECT
    CUSTOMER_ID,
    COUNT(*) AS ORDER_COUNT,
    SUM(TOTAL_AMOUNT) AS LIFETIME_VALUE
FROM PRODUCTION.ORDERS
GROUP BY CUSTOMER_ID
HAVING LIFETIME_VALUE > 1000
ORDER BY LIFETIME_VALUE DESC;
```

### Exemple 3 : Out of stock products de stock

```sql
SELECT
    PRODUCT_NAME,
    PRODUCT_CATEGORY,
    CURRENT_STOCK_LEVEL,
    WAREHOUSE_LOCATION
FROM PRODUCTION.INVENTORY_CURRENT
WHERE CURRENT_STOCK_LEVEL = 0
ORDER BY PRODUCT_CATEGORY;
```

---

## 📊 Monitoring en temps réel

### Verify l'état du pipeline

```sql
-- 1. État des tasks
SHOW TASKS IN SCHEMA RAW_DATA;

-- 2. Historique des exécutions (dernières 10)
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

-- 3. Verify les streams (données en attente)
SELECT 'STREAM_RAW_ORDERS' AS STREAM_NAME, 
       SYSTEM$STREAM_HAS_DATA('STREAM_RAW_ORDERS') AS HAS_DATA
UNION ALL
SELECT 'STREAM_RAW_INVENTORY', 
       SYSTEM$STREAM_HAS_DATA('STREAM_RAW_INVENTORY');

-- 4. Pipeline latency
SELECT
    MAX(INGESTION_TIMESTAMP) AS LAST_RAW_INGESTION,
    MAX(UPDATED_AT) AS LAST_PROD_UPDATE,
    DATEDIFF('minute', MAX(UPDATED_AT), CURRENT_TIMESTAMP()) AS LATENCY_MINUTES
FROM PRODUCTION.ORDERS;
```

### Dashboard de santé

```sql
-- Vue d'ensemble du nombre de lignes par table
SELECT 'RAW_EVENTS_STREAM' AS TABLE_NAME, COUNT(*) AS ROW_COUNT FROM RAW_DATA.RAW_EVENTS_STREAM
UNION ALL
SELECT 'STG_ORDERS', COUNT(*) FROM STAGING.STG_ORDERS
UNION ALL
SELECT 'STG_INVENTORY_ADJ', COUNT(*) FROM STAGING.STG_INVENTORY_ADJUSTMENTS
UNION ALL
SELECT 'ORDERS', COUNT(*) FROM PRODUCTION.ORDERS
UNION ALL
SELECT 'INVENTORY_CURRENT', COUNT(*) FROM PRODUCTION.INVENTORY_CURRENT
UNION ALL
SELECT 'INVENTORY_HISTORY', COUNT(*) FROM PRODUCTION.INVENTORY_HISTORY;
```

---

## 🛠️ Commandes de gestion

### Suspendre temporairement les tasks

```sql
-- Suspendre dans l'ordre inverse (enfants d'abord)
ALTER TASK TASK_STAGING_TO_PROD_INVENTORY_CURRENT SUSPEND;
ALTER TASK TASK_STAGING_TO_PROD_INVENTORY_HISTORY SUSPEND;
ALTER TASK TASK_STAGING_TO_PROD_ORDERS SUSPEND;
ALTER TASK TASK_RAW_TO_STAGING_INVENTORY SUSPEND;
ALTER TASK TASK_RAW_TO_STAGING_ORDERS SUSPEND;
```

### Réactivate les tasks

```sql
-- Activate dans l'ordre normal (parents d'abord)
ALTER TASK TASK_RAW_TO_STAGING_ORDERS RESUME;
ALTER TASK TASK_RAW_TO_STAGING_INVENTORY RESUME;
ALTER TASK TASK_STAGING_TO_PROD_ORDERS RESUME;
ALTER TASK TASK_STAGING_TO_PROD_INVENTORY_HISTORY RESUME;
ALTER TASK TASK_STAGING_TO_PROD_INVENTORY_CURRENT RESUME;
```

### Execute manuellement une task (test)

```sql
EXECUTE TASK TASK_RAW_TO_STAGING_ORDERS;
```

### Clean les old data

```sql
-- Delete les données RAW de more than 30 jours
DELETE FROM RAW_DATA.RAW_EVENTS_STREAM
WHERE INGESTION_TIMESTAMP < DATEADD('day', -30, CURRENT_TIMESTAMP());

-- Delete les données STAGING de more than 7 jours
DELETE FROM STAGING.STG_ORDERS
WHERE INGESTION_TIMESTAMP < DATEADD('day', -7, CURRENT_TIMESTAMP());
```

---

## 🔧 Troubleshooting

### Problème : Les tasks ne s'exécutent pas

```sql
-- 1. Verify l'état des tasks
SHOW TASKS;

-- 2. Voir les erreurs
SELECT NAME, ERROR_CODE, ERROR_MESSAGE, QUERY_TEXT
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY())
WHERE STATE = 'FAILED'
ORDER BY SCHEDULED_TIME DESC
LIMIT 5;

-- 3. Réactivate si nécessaire
ALTER TASK TASK_RAW_TO_STAGING_ORDERS RESUME;
```

### Problème : Les streams sont vides

```sql
-- Verify que des données arrivent dans RAW
SELECT COUNT(*) FROM RAW_DATA.RAW_EVENTS_STREAM
WHERE INGESTION_TIMESTAMP > DATEADD('minute', -5, CURRENT_TIMESTAMP());

-- Si 0 : Verify que le consumer Kafka fonctionne
-- docker logs consumer-caves-albert
```

### Problème : Latence excessive (> 5 min)

```sql
-- Verify la durée d'exécution des tasks
SELECT
    NAME,
    DATEDIFF('second', SCHEDULED_TIME, COMPLETED_TIME) AS DURATION_SEC
FROM TABLE(INFORMATION_SCHEMA.TASK_HISTORY())
WHERE NAME LIKE 'TASK_%'
    AND SCHEDULED_TIME > DATEADD('hour', -1, CURRENT_TIMESTAMP())
ORDER BY DURATION_SEC DESC;

-- Si trop long : Augmenter la taille du warehouse
-- ALTER WAREHOUSE COMPUTE_WH SET WAREHOUSE_SIZE = 'MEDIUM';
```

---

## 💰 Optimisation des coûts

### Stratégies

1. **Tasks conditionnelles** : Les tasks ne s'exécutent que si `SYSTEM$STREAM_HAS_DATA() = TRUE`
2. **Auto-suspend warehouse** : Le warehouse se suspend automatiquement entre les exécutions
3. **Nettoyage régulier** : Delete les old data RAW et STAGING
4. **Clustering keys** : Add des clés de clustering sur les grandes tables

### Exemple de clustering

```sql
-- Optimiser les requêtes par date
ALTER TABLE PRODUCTION.ORDERS 
CLUSTER BY (ORDER_DATE);

-- Optimiser les requêtes par produit
ALTER TABLE PRODUCTION.INVENTORY_CURRENT 
CLUSTER BY (PRODUCT_CATEGORY, PRODUCT_ID);
```

---

## 📚 Documentation

- **`SNOWFLAKE_AUTOMATION_GUIDE.md`** : Guide complet avec explications détaillées
- **`ARCHITECTURE_DIAGRAM.md`** : Diagrammes visuels du flux de données
- **`analytical-queries.sql`** : Toutes les requêtes prêtes à l'emploi

### Resources externes

- [Snowflake Streams Documentation](https://docs.snowflake.com/en/user-guide/streams-intro)
- [Snowflake Tasks Documentation](https://docs.snowflake.com/en/user-guide/tasks-intro)
- [CDC with Streams](https://docs.snowflake.com/en/user-guide/streams-cdc)

---

## 🎯 Avantages de cette architecture

### ✅ Temps réel
- Latence < 3 minutes de bout en bout
- Données disponibles pour l'analytique quasi instantanément
- Support de millions d'événements par jour

### ✅ Fiabilité
- CDC natif avec Snowflake Streams
- Garantie exactly-once processing
- Traçabilité complète avec timestamps

### ✅ Scalabilité
- Architecture modulaire (RAW → STAGING → PROD)
- Facile d'add de nouveaux types d'événements
- Support de la croissance du volume de données

### ✅ Maintenabilité
- SQL pur, pas de code externe
- Monitoring intégré
- Facile à débugger et à modify

### ✅ Coût optimisé
- Tasks conditionnelles (uniquement si données présentes)
- Warehouse auto-suspend
- Pas de crédits Snowflake gaspillés

---

## 🚀 Prochaines étapes

### Améliorations recommandées

1. **Alerting** : Configurer des alertes Snowflake pour les anomalies
2. **DBT** : Intégrer DBT pour la gestion des transformations
3. **Great Expectations** : Add des tests de qualité de données
4. **Tableau/Power BI** : Connecter un outil BI pour des dashboards visuels
5. **Machine Learning** : Prévisions de demande avec Snowflake ML

### Intégrations possibles

- **Salesforce** : Synchroniser les données clients
- **Shopify** : Intégrer les commandes e-commerce
- **Google Analytics** : Enrichir avec les données web
- **SendGrid** : Automatiser les emails marketing

---

## 👥 Support

Pour toute question ou assistance :

- 📧 Email : data-team@lescavesdalbert.com
- 📚 Documentation : Lire `SNOWFLAKE_AUTOMATION_GUIDE.md`
- 🐛 Issues : Ouvrir un ticket sur GitHub

---

## 📄 Licence

MIT License - Libre d'utilisation et de modification

---

**🍷 Bon traitement de données avec Les Caves d'Albert !**

*Créé avec ❤️ pour démontrer les meilleures pratiques Snowflake en production*
