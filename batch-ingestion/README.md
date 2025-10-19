# 📦 Batch Ingestion - Les Caves d'Albert

Ce dossier contient les **notebooks et scripts d'ingestion en batch** pour le projet Les Caves d'Albert.

---

## 📋 Contenu

### Notebooks Jupyter

#### `Data_generator_faker.ipynb`
**Générateur de données de vente de vin avec Faker**

- **Objectif**: Générer des données de vente réalistes pour tests et démonstrations
- **Sortie**: Base de données SQLite (`wine_data.db`) avec tables `customers`, `inventory`, `sales`
- **Technologies**: Python, Faker, SQLite, Pandas
- **Données générées**:
  - 50 produits (vins et spiritueux) avec catégories, prix, tailles de bouteilles
  - 100+ clients avec noms français (Faker locale `fr_FR`)
  - Transactions de vente sur 10 jours avec logique de stock
- **Seed**: 11 (reproductibilité garantie)

**Structure des données**:
```sql
-- Table customers
customer_id, name, email, registration_date

-- Table inventory
product_id, product_name, category, price_per_unit, bottle_size_liters, stock_quantity

-- Table sales
sale_id, sale_date, customer_id, product_id, quantity_sold, total_price, sales_channel
```

#### `Pipeline.ipynb`
**Pipeline d'ingestion SQLite → Snowflake**

- **Objectif**: Charger les données batch depuis SQLite vers Snowflake
- **Architecture**: ELT (Extract, Load, Transform)
- **Étapes**:
  1. **Extract**: Lecture des tables SQLite (`customers`, `inventory`, `sales`)
  2. **Load**: Insertion dans Snowflake via `pandas.to_sql()` + SQLAlchemy
  3. **Transform**: Transformations SQL dans Snowflake (optionnel)
- **Technologies**: Python, SQLite, Snowflake, SQLAlchemy, Pandas
- **Sécurité**: Utilise `.env` pour credentials Snowflake (via `python-dotenv`)

**Configuration requise** (`.env`):
```bash
# Source SQLite
DB_PATH=test_data/wine_data.db

# Target Snowflake
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account.region
SNOWFLAKE_WAREHOUSE=COMPUTE_WH
SNOWFLAKE_DATABASE=WINE_SALES_DB
SNOWFLAKE_SCHEMA=BATCH_DATA
```

---

### Autres fichiers

#### `Git_Basics.ipynb`
**Tutoriel Git pour débutants**

- Guide d'installation et configuration Git
- Commandes de base (init, add, commit, push, pull)
- Workflow Git standard
- Configuration VSCode comme éditeur par défaut

#### `Screenshot Snwoflake.png`
**Capture d'écran Snowflake**

- Screenshot historique de l'interface Snowflake
- Utile pour documentation visuelle

---

## 🔄 Différence Batch vs Streaming

| Aspect | Batch Ingestion (ce dossier) | Streaming (`/streaming`) |
|--------|------------------------------|--------------------------|
| **Fréquence** | Manuel ou schedulé (quotidien, hebdomadaire) | En temps réel (continu) |
| **Volume** | Gros volumes (historique) | Événements individuels |
| **Latence** | Minutes à heures | Millisecondes à secondes |
| **Cas d'usage** | Chargement initial, rapports mensuels | Analytics temps réel, alertes |
| **Technologies** | SQLite, Pandas, Notebooks | Kafka, RedPanda, Producer/Consumer |
| **Source** | `wine_data.db` (SQLite) | Kafka topic `sales_events` |
| **Destination** | Snowflake schema `BATCH_DATA` | Snowflake schema `RAW_DATA` |

---

## 🚀 Utilisation

### 1. Générer les données (Data_generator_faker.ipynb)

```bash
# Dans VSCode, ouvrir le notebook et exécuter toutes les cellules
# Ou en ligne de commande:
jupyter notebook Data_generator_faker.ipynb
```

Cela créera `test_data/wine_data.db` avec ~100 clients, 50 produits, et transactions sur 10 jours.

### 2. Charger vers Snowflake (Pipeline.ipynb)

**Prérequis**:
- Fichier `.env` configuré avec credentials Snowflake
- Base de données `wine_data.db` générée

```bash
jupyter notebook Pipeline.ipynb
```

Le notebook va:
1. Se connecter à SQLite (`wine_data.db`)
2. Extraire les 3 tables
3. Se connecter à Snowflake
4. Créer les tables si elles n'existent pas
5. Insérer les données

---

## 📊 Schéma Snowflake (Batch)

```sql
-- Database: WINE_SALES_DB
-- Schema: BATCH_DATA

-- Table customers (dimension)
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name VARCHAR(200),
    email VARCHAR(200),
    registration_date DATE
);

-- Table inventory (dimension)
CREATE TABLE inventory (
    product_id INTEGER PRIMARY KEY,
    product_name VARCHAR(200),
    category VARCHAR(50),
    price_per_unit DECIMAL(10,2),
    bottle_size_liters DECIMAL(5,3),
    stock_quantity INTEGER
);

-- Table sales (fait)
CREATE TABLE sales (
    sale_id INTEGER PRIMARY KEY,
    sale_date TIMESTAMP,
    customer_id INTEGER,
    product_id INTEGER,
    quantity_sold INTEGER,
    total_price DECIMAL(10,2),
    sales_channel VARCHAR(100)
);
```

---

## 🔗 Relation avec le Streaming

Les données batch servent de **baseline historique**, tandis que le streaming (`/streaming`) capture les **événements temps réel**.

**Exemple de workflow combiné**:
1. **Batch** (ce dossier): Charger 1 an d'historique de ventes via `Pipeline.ipynb`
2. **Streaming** (`/streaming`): À partir d'aujourd'hui, ingérer les nouvelles ventes en temps réel via Kafka

**Consolidation dans Snowflake**:
```sql
-- Vue combinée batch + streaming
CREATE VIEW consolidated_sales AS
SELECT 
    sale_date,
    customer_id,
    product_id,
    quantity_sold,
    total_price,
    'BATCH' as source
FROM BATCH_DATA.sales

UNION ALL

SELECT 
    PARSE_JSON(event_content):timestamp::TIMESTAMP as sale_date,
    PARSE_JSON(event_content):customer_id::INTEGER as customer_id,
    PARSE_JSON(event_content):product_id::INTEGER as product_id,
    PARSE_JSON(event_content):quantity::INTEGER as quantity_sold,
    PARSE_JSON(event_content):total_price::DECIMAL(10,2) as total_price,
    'STREAMING' as source
FROM RAW_DATA.raw_events_stream
WHERE event_type = 'ORDER_CREATED';
```

---

## 📚 Dépendances

```bash
# Pour Data_generator_faker.ipynb
pip install faker pandas

# Pour Pipeline.ipynb
pip install pandas sqlalchemy snowflake-sqlalchemy python-dotenv

# Pour exécuter les notebooks
pip install jupyter notebook
```

---

## 🛠️ Troubleshooting

**Problème**: `wine_data.db` n'existe pas
- ✅ Exécuter d'abord `Data_generator_faker.ipynb` pour générer la base

**Problème**: Erreur de connexion Snowflake dans `Pipeline.ipynb`
- ✅ Vérifier le fichier `.env` avec les bons credentials
- ✅ Tester la connexion : `snowsql -a <account> -u <user>`

**Problème**: `ModuleNotFoundError: No module named 'faker'`
- ✅ Installer les dépendances : `pip install faker pandas jupyter`

---

**Pour le streaming temps réel, voir le dossier `/streaming` 🚀**
