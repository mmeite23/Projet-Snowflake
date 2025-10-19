# 🍷 Guide de Déploiement - Dashboard Streamlit in Snowflake

## 📋 Vue d'ensemble

Ce dashboard Streamlit s'exécute **directement dans Snowflake** (Streamlit in Snowflake) pour analyser les données en temps réel de "Les Caves d'Albert".

### ✨ Fonctionnalités

- 📊 **5 KPIs principaux** : Commandes, Clients, CA, Panier moyen, Articles vendus
- 🍷 **Top 10 des vins** les plus vendus
- 📈 **Analyse par catégorie** (Rouge, Blanc, Effervescent, Spiritueux)
- 📅 **Évolution temporelle** du chiffre d'affaires
- 👥 **Top clients** par montant dépensé
- ⚠️ **Alertes stock** (produits < 50 unités)
- 🔄 **Mouvements d'inventaire** récents
- 🎛️ **Filtres interactifs** : période, catégories

---

## 🚀 Déploiement dans Snowflake

### **Prérequis**

✅ Compte Snowflake avec **Streamlit in Snowflake** activé  
✅ Base de données `CAVES_ALBERT_DB` avec données PRODUCTION  
✅ Rôle avec accès à PRODUCTION.ORDERS et PRODUCTION.INVENTORY_*

---

### **Étape 1 : Créer le Streamlit App dans Snowflake**

1. **Connectez-vous à Snowflake**
2. Dans le menu de gauche, cliquez sur **Streamlit**
3. Cliquez sur **+ Streamlit App**
4. Configurez :
   - **App name** : `Les_Caves_Albert_Dashboard`
   - **Warehouse** : `COMPUTE_WH`
   - **App location** :
     - Database : `CAVES_ALBERT_DB`
     - Schema : `PUBLIC` ou créez `DASHBOARDS`

---

### **Étape 2 : Copier le code**

1. Ouvrez le fichier `streamlit_dashboard_snowflake.py`
2. **Copiez TOUT le contenu**
3. **Collez** dans l'éditeur Streamlit de Snowflake
4. Cliquez sur **Run** (coin supérieur droit)

---

### **Étape 3 : Vérification**

Le dashboard devrait afficher :

✅ 5 métriques KPI en haut  
✅ Graphique des top 10 vins  
✅ Graphique des ventes par catégorie  
✅ Évolution du CA dans le temps  
✅ Alertes stock faible  

---

## 🎨 Personnalisation

### **Modifier les filtres de période**

Dans la sidebar, section "Période d'analyse" :

```python
time_mapping = {
    "Dernières 24h": "DATEADD('day', -1, CURRENT_TIMESTAMP())",
    "7 derniers jours": "DATEADD('day', -7, CURRENT_TIMESTAMP())",
    "30 derniers jours": "DATEADD('day', -30, CURRENT_TIMESTAMP())",
    "Tout l'historique": "DATEADD('year', -10, CURRENT_TIMESTAMP())"
}
```

Ajoutez vos propres périodes !

---

### **Modifier les seuils d'alerte stock**

Ligne ~290, changez la valeur de 50 :

```python
WHERE CURRENT_STOCK_LEVEL < 50  # ← Changez cette valeur
```

---

### **Ajouter un nouveau graphique**

Exemple : Ajouter un graphique "Ventes par canal" (E-com, Boutique, etc.)

```python
st.subheader("📊 Ventes par Canal")
channel_sales = session.sql(f"""
    SELECT 
        PAYMENT_METHOD AS CANAL,
        COUNT(*) AS ORDERS,
        ROUND(SUM(TOTAL_AMOUNT), 2) AS REVENUE
    FROM PRODUCTION.ORDERS
    WHERE ORDER_TIMESTAMP >= {time_filter}
    GROUP BY PAYMENT_METHOD
    ORDER BY REVENUE DESC
""").to_pandas()

st.bar_chart(channel_sales.set_index('CANAL')['REVENUE'])
```

---

## 📊 Utilisation

### **Filtres disponibles**

1. **Période** : Dernières 24h / 7j / 30j / Tout l'historique
2. **Catégories** : Rouge, Blanc, Effervescent, Spiritueux (multi-sélection)

### **Rafraîchir les données**

Cliquez sur le bouton **🔄 Actualiser les données** dans la sidebar.

---

## 🔧 Dépannage

### **Erreur : "Table does not exist"**

**Cause** : Les tables PRODUCTION n'existent pas ou ne sont pas accessibles

**Solution** :
```sql
-- Vérifier que les tables existent
USE DATABASE CAVES_ALBERT_DB;
SELECT COUNT(*) FROM PRODUCTION.ORDERS;
SELECT COUNT(*) FROM PRODUCTION.INVENTORY_CURRENT;
SELECT COUNT(*) FROM PRODUCTION.INVENTORY_HISTORY;
```

---

### **Erreur : "Cannot get active session"**

**Cause** : Le code n'est pas exécuté dans Streamlit in Snowflake

**Solution** : Assurez-vous d'utiliser **Streamlit in Snowflake** (pas un Streamlit local)

---

### **Graphiques vides**

**Cause** : Aucune donnée pour la période sélectionnée

**Solution** :
1. Sélectionnez "Tout l'historique"
2. Vérifiez que les tasks Snowflake ont bien propagé les données
3. Exécutez : `SELECT COUNT(*) FROM PRODUCTION.ORDERS;`

---

## 🎯 Prochaines Améliorations

### **Version 2 : Fonctionnalités avancées**

- [ ] 📧 Alertes email pour stock critique
- [ ] 🔮 Prédictions de ventes (ML)
- [ ] 📍 Carte géographique des entrepôts
- [ ] 💰 Analyse de marge par produit
- [ ] 📊 Exports PDF des rapports
- [ ] 🔔 Notifications en temps réel

### **Exemples de widgets à ajouter**

```python
# Widget : Sélecteur de date personnalisé
date_range = st.date_input(
    "Sélectionner une plage de dates",
    value=(datetime.now() - timedelta(days=30), datetime.now())
)

# Widget : Recherche de produit
search_product = st.text_input("🔍 Rechercher un produit")

# Widget : Export CSV
if st.button("📥 Télécharger les données"):
    csv = top_products.to_csv(index=False)
    st.download_button(
        label="💾 Download CSV",
        data=csv,
        file_name="top_products.csv",
        mime="text/csv"
    )
```

---

## 📱 Partage du Dashboard

### **Option 1 : Partage interne Snowflake**

1. Dans Streamlit in Snowflake, cliquez sur **Share**
2. Sélectionnez les rôles/utilisateurs autorisés
3. Ils accéderont via leur compte Snowflake

### **Option 2 : URL publique (si disponible)**

Certains comptes Snowflake permettent de générer une URL publique.

---

## 🔗 Ressources

- [Streamlit in Snowflake Documentation](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
- [Snowpark Python API](https://docs.snowflake.com/en/developer-guide/snowpark/python/index)
- [Streamlit API Reference](https://docs.streamlit.io/library/api-reference)

---

## ✅ Checklist de Déploiement

- [ ] Base de données CAVES_ALBERT_DB créée
- [ ] Tables PRODUCTION.ORDERS, INVENTORY_CURRENT, INVENTORY_HISTORY remplies
- [ ] Streamlit in Snowflake activé sur le compte
- [ ] Warehouse COMPUTE_WH disponible
- [ ] Code copié dans l'éditeur Streamlit
- [ ] Dashboard s'affiche correctement
- [ ] Filtres fonctionnent
- [ ] Graphiques affichent des données
- [ ] Dashboard partagé avec l'équipe

---

**🍷 Profitez de votre dashboard BI en temps réel ! 🍷**
