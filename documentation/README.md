# 📚 Documentation - Les Caves d'Albert

Ce dossier contient toute la documentation technique du projet Snowflake.

## 📖 Table des Matières

### 🚀 Guides de Démarrage

| Fichier | Description | À lire si... |
|---------|-------------|--------------|
| **[QUICKSTART.md](./QUICKSTART.md)** | Démarrage rapide en 3 étapes | Vous débutez le projet |
| **[QUICK_START.md](./QUICK_START.md)** | Guide de démarrage original | Référence historique |
| **[README-DEPLOYMENT.md](./README-DEPLOYMENT.md)** | Guide complet de déploiement (200+ lignes) | Vous voulez tous les détails |

### 🏗️ Architecture

| Fichier | Description | Contenu |
|---------|-------------|---------|
| **[ARCHITECTURE_DIAGRAM.md](./ARCHITECTURE_DIAGRAM.md)** | Diagrammes visuels du pipeline | Schémas RAW → STAGING → PRODUCTION |
| **[ARCHITECTURE_PHILOSOPHY.md](./ARCHITECTURE_PHILOSOPHY.md)** | Philosophie et principes de conception | Comprendre les choix techniques |

### ⚙️ Configuration Snowflake

| Fichier | Description | À utiliser pour... |
|---------|-------------|-------------------|
| **[SNOWFLAKE_AUTOMATION_GUIDE.md](./SNOWFLAKE_AUTOMATION_GUIDE.md)** | Guide d'automatisation avec Tasks & Streams | Comprendre le CDC et l'automatisation |
| **[SNOWFLAKE_TASKS_README.md](./SNOWFLAKE_TASKS_README.md)** | Documentation des Tasks Snowflake | Référence des tasks créées |

### 🔧 Configuration Kafka & Streaming

| Fichier | Description | Contenu |
|---------|-------------|---------|
| **[KAFKA_PRODUCER_IMPROVEMENTS.md](./KAFKA_PRODUCER_IMPROVEMENTS.md)** | Améliorations du producer Kafka | Optimisations et fonctionnalités |
| **[KAFKA_CONSUMER_README.md](./KAFKA_CONSUMER_README.md)** | Documentation du consumer | Configuration et utilisation |
| **[CONSUMER_IMPROVEMENTS.md](./CONSUMER_IMPROVEMENTS.md)** | Améliorations du consumer | Évolutions et performances |

### 📊 Exemples et Outputs

| Fichier | Description | Contenu |
|---------|-------------|---------|
| **[SAMPLE_OUTPUT.md](./SAMPLE_OUTPUT.md)** | Exemples de sorties du pipeline | Logs et résultats attendus |

---

## 🎯 Par où commencer ?

### **Niveau 1 : Démarrage Rapide (5 minutes)**
1. Lisez [QUICKSTART.md](./QUICKSTART.md)
2. Exécutez le script SQL
3. Vérifiez que ça marche

### **Niveau 2 : Compréhension Approfondie (20 minutes)**
1. Lisez [README-DEPLOYMENT.md](./README-DEPLOYMENT.md)
2. Consultez [ARCHITECTURE_DIAGRAM.md](./ARCHITECTURE_DIAGRAM.md)
3. Explorez [SNOWFLAKE_AUTOMATION_GUIDE.md](./SNOWFLAKE_AUTOMATION_GUIDE.md)

### **Niveau 3 : Maintenance et Monitoring (30+ minutes)**
1. Étudiez [SNOWFLAKE_TASKS_README.md](./SNOWFLAKE_TASKS_README.md)
2. Testez les requêtes de monitoring
3. Personnalisez le pipeline selon vos besoins

---

## 📊 Structure du Projet

```
Projet-Snowflake/
├── documentation/              # 📚 Ce dossier
│   ├── README.md              # Index (ce fichier)
│   ├── QUICKSTART.md          # Guide rapide
│   ├── README-DEPLOYMENT.md   # Guide complet
│   ├── ARCHITECTURE_DIAGRAM.md # Diagrammes
│   ├── SNOWFLAKE_AUTOMATION_GUIDE.md
│   └── SNOWFLAKE_TASKS_README.md
│
├── streaming/                  # Code Python
│   ├── kafka_producer.py      # Génère les événements
│   └── kafka_consumer_snowflake.py # Ingestion Snowflake
│
├── *.sql                       # Scripts SQL
│   ├── snowflake-tasks-streams-CORRECTED.sql ⭐
│   ├── analytical-queries.sql
│   ├── fix-*.sql
│   └── execute-tasks-now.sql
│
└── docker-compose.yml          # Infrastructure
```

---

## 🔗 Liens Rapides

### Scripts SQL Principaux
- 🎯 **[../snowflake-tasks-streams-CORRECTED.sql](../snowflake-tasks-streams-CORRECTED.sql)** - Script principal à exécuter
- 📊 **[../analytical-queries.sql](../analytical-queries.sql)** - 50+ requêtes analytiques
- 🔧 **[../execute-tasks-now.sql](../execute-tasks-now.sql)** - Exécution manuelle des tasks

### Interfaces Web
- 🍷 **Grafana** : http://localhost:3000 (admin/admin)
- 📊 **RedPanda Console** : http://localhost:8080
- 📈 **Prometheus** : http://localhost:9090
- 🔍 **Consumer Metrics** : http://localhost:8000/metrics

---

## 📞 Support

Si vous rencontrez des problèmes :
1. Consultez la section "Problèmes Courants" dans [README-DEPLOYMENT.md](./README-DEPLOYMENT.md)
2. Vérifiez les logs : `docker logs consumer --tail 100`
3. Vérifiez l'état des tasks dans Snowflake

---

**🍷 Bon développement avec Les Caves d'Albert ! 🍷**
