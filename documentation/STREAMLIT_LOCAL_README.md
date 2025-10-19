# 🍷 Dashboard Streamlit - Les Caves d'Albert (Version Locale)

## 📋 Installation

### Prerequisites
```bash
pip install streamlit snowflake-connector-python pandas plotly
```

### Fichier de configuration `.streamlit/secrets.toml`

Créez un fichier `.streamlit/secrets.toml` à la racine du projet :

```toml
[snowflake]
user = "VOTRE_USER"
password = "VOTRE_PASSWORD"
account = "VOTRE_ACCOUNT"
warehouse = "COMPUTE_WH"
database = "CAVES_ALBERT_DB"
schema = "PRODUCTION"
role = "VOTRE_ROLE"
```

## 🚀 Lancement

### Option 1 : Dans Snowflake (Recommandé)
Voir `STREAMLIT_DASHBOARD_GUIDE.md`

### Option 2 : En local
```bash
streamlit run streamlit_dashboard_local.py
```

Le dashboard s'ouvrira automatiquement dans votre navigateur sur http://localhost:8501

## 📊 Fonctionnalités

- ✅ KPIs en temps réel
- ✅ Graphiques interactifs
- ✅ Filtres par période et catégorie
- ✅ Alertes stock
- ✅ Analyse des tendances

## 🔧 Différences Local vs Snowflake

| Fonctionnalité | Local | Snowflake |
|---------------|-------|-----------|
| Installation | Pip + secrets.toml | Aucune |
| Performance | Dépend du réseau | Très rapide |
| Sécurité | Credentials locaux | Intégré SSO |
| Partage | Difficile | Natif |
| **Recommandation** | Dev/Test | **Production** ✅ |

## ⚠️ Note

Pour la **production**, utilisez **Streamlit in Snowflake** (voir `STREAMLIT_DASHBOARD_GUIDE.md`).

Cette version locale est uniquement pour le **développement et les tests**.
