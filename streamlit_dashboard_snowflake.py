# 🍷 Les Caves d'Albert - Dashboard BI Streamlit in Snowflake

import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session

# Configuration de la page
st.set_page_config(
    page_title="🍷 Les Caves d'Albert - Dashboard BI",
    page_icon="🍷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Obtenir la session Snowflake active
session = get_active_session()

# ============================================
# STYLES CSS PERSONNALISÉS
# ============================================
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #8B0000;
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        color: white;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .stMetric {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# HEADER
# ============================================
st.markdown('<h1 class="main-header">🍷 Les Caves d\'Albert - Business Intelligence Dashboard</h1>', unsafe_allow_html=True)
st.markdown("---")

# ============================================
# SIDEBAR - FILTRES
# ============================================
with st.sidebar:
    st.image("https://em-content.zobj.net/thumbs/120/apple/354/wine-glass_1f377.png", width=100)
    st.title("📊 Filtres")
    
    # Période de temps
    time_range = st.selectbox(
        "Période d'analyse",
        ["Dernières 24h", "7 derniers jours", "30 derniers jours", "Tout l'historique"]
    )
    
    # Mapping des périodes
    time_mapping = {
        "Dernières 24h": "DATEADD('day', -1, CURRENT_TIMESTAMP())",
        "7 derniers jours": "DATEADD('day', -7, CURRENT_TIMESTAMP())",
        "30 derniers jours": "DATEADD('day', -30, CURRENT_TIMESTAMP())",
        "Tout l'historique": "DATEADD('year', -10, CURRENT_TIMESTAMP())"
    }
    time_filter = time_mapping[time_range]
    
    # Catégorie de produit
    categories = session.sql("""
        SELECT DISTINCT PRODUCT_CATEGORY 
        FROM PRODUCTION.ORDERS 
        WHERE PRODUCT_CATEGORY IS NOT NULL
        ORDER BY PRODUCT_CATEGORY
    """).to_pandas()
    
    selected_categories = st.multiselect(
        "Catégories de produits",
        options=categories['PRODUCT_CATEGORY'].tolist(),
        default=categories['PRODUCT_CATEGORY'].tolist()
    )
    
    st.markdown("---")
    st.markdown("### 🔄 Rafraîchir")
    if st.button("🔄 Actualiser les données", use_container_width=True):
        st.rerun()

# ============================================
# MÉTRIQUES CLÉS (KPIs)
# ============================================
st.header("📈 Indicateurs Clés de Performance")

# Construire le filtre de catégories
category_filter = "AND PRODUCT_CATEGORY IN (" + ",".join([f"'{cat}'" for cat in selected_categories]) + ")" if selected_categories else ""

# Requête KPIs
kpi_query = f"""
SELECT 
    COUNT(DISTINCT ORDER_ID) AS TOTAL_ORDERS,
    COUNT(DISTINCT CUSTOMER_ID) AS TOTAL_CUSTOMERS,
    ROUND(SUM(TOTAL_AMOUNT), 2) AS TOTAL_REVENUE,
    ROUND(AVG(TOTAL_AMOUNT), 2) AS AVG_ORDER_VALUE,
    SUM(QUANTITY) AS TOTAL_ITEMS_SOLD
FROM PRODUCTION.ORDERS
WHERE ORDER_TIMESTAMP >= {time_filter}
{category_filter}
"""

kpis = session.sql(kpi_query).to_pandas().iloc[0]

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="🛒 Commandes",
        value=f"{int(kpis['TOTAL_ORDERS']):,}",
        delta="Total"
    )

with col2:
    st.metric(
        label="👥 Clients",
        value=f"{int(kpis['TOTAL_CUSTOMERS']):,}",
        delta="Uniques"
    )

with col3:
    st.metric(
        label="💰 Chiffre d'affaires",
        value=f"€{kpis['TOTAL_REVENUE']:,.2f}",
        delta=f"Total"
    )

with col4:
    st.metric(
        label="🧾 Panier moyen",
        value=f"€{kpis['AVG_ORDER_VALUE']:,.2f}",
        delta="Par commande"
    )

with col5:
    st.metric(
        label="📦 Articles vendus",
        value=f"{int(kpis['TOTAL_ITEMS_SOLD']):,}",
        delta="Total"
    )

st.markdown("---")

# ============================================
# GRAPHIQUES - LIGNE 1
# ============================================
st.header("📊 Analyse des Ventes")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🍷 Top 10 des Vins les Plus Vendus")
    top_products = session.sql(f"""
        SELECT 
            PRODUCT_NAME,
            PRODUCT_CATEGORY,
            COUNT(*) AS ORDER_COUNT,
            SUM(QUANTITY) AS TOTAL_QUANTITY,
            ROUND(SUM(TOTAL_AMOUNT), 2) AS TOTAL_REVENUE
        FROM PRODUCTION.ORDERS
        WHERE ORDER_TIMESTAMP >= {time_filter}
        {category_filter}
        GROUP BY PRODUCT_NAME, PRODUCT_CATEGORY
        ORDER BY TOTAL_REVENUE DESC
        LIMIT 10
    """).to_pandas()
    
    if not top_products.empty:
        st.bar_chart(
            top_products.set_index('PRODUCT_NAME')['TOTAL_REVENUE'],
            use_container_width=True
        )
        st.dataframe(
            top_products.style.format({
                'TOTAL_REVENUE': '€{:,.2f}',
                'ORDER_COUNT': '{:,.0f}',
                'TOTAL_QUANTITY': '{:,.0f}'
            }),
            use_container_width=True
        )
    else:
        st.info("Aucune donnée disponible pour cette période")

with col2:
    st.subheader("📊 Ventes par Catégorie")
    category_sales = session.sql(f"""
        SELECT 
            PRODUCT_CATEGORY,
            COUNT(*) AS ORDER_COUNT,
            ROUND(SUM(TOTAL_AMOUNT), 2) AS TOTAL_REVENUE
        FROM PRODUCTION.ORDERS
        WHERE ORDER_TIMESTAMP >= {time_filter}
        {category_filter}
        GROUP BY PRODUCT_CATEGORY
        ORDER BY TOTAL_REVENUE DESC
    """).to_pandas()
    
    if not category_sales.empty:
        st.bar_chart(
            category_sales.set_index('PRODUCT_CATEGORY')['TOTAL_REVENUE'],
            use_container_width=True
        )
        st.dataframe(
            category_sales.style.format({
                'TOTAL_REVENUE': '€{:,.2f}',
                'ORDER_COUNT': '{:,.0f}'
            }),
            use_container_width=True
        )
    else:
        st.info("Aucune donnée disponible")

st.markdown("---")

# ============================================
# GRAPHIQUES - LIGNE 2
# ============================================
st.header("📈 Tendances Temporelles")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📅 Évolution du Chiffre d'Affaires")
    daily_sales = session.sql(f"""
        SELECT 
            ORDER_DATE,
            COUNT(*) AS ORDER_COUNT,
            ROUND(SUM(TOTAL_AMOUNT), 2) AS DAILY_REVENUE
        FROM PRODUCTION.ORDERS
        WHERE ORDER_TIMESTAMP >= {time_filter}
        {category_filter}
        GROUP BY ORDER_DATE
        ORDER BY ORDER_DATE DESC
        LIMIT 30
    """).to_pandas()
    
    if not daily_sales.empty:
        daily_sales = daily_sales.sort_values('ORDER_DATE')
        st.line_chart(
            daily_sales.set_index('ORDER_DATE')['DAILY_REVENUE'],
            use_container_width=True
        )
        st.caption(f"📊 Tendance sur les {len(daily_sales)} derniers jours")
    else:
        st.info("Aucune donnée disponible")

with col2:
    st.subheader("👥 Top 10 Clients (par CA)")
    top_customers = session.sql(f"""
        SELECT 
            CUSTOMER_ID,
            COUNT(*) AS ORDER_COUNT,
            SUM(QUANTITY) AS TOTAL_ITEMS,
            ROUND(SUM(TOTAL_AMOUNT), 2) AS TOTAL_SPENT
        FROM PRODUCTION.ORDERS
        WHERE ORDER_TIMESTAMP >= {time_filter}
        {category_filter}
        GROUP BY CUSTOMER_ID
        ORDER BY TOTAL_SPENT DESC
        LIMIT 10
    """).to_pandas()
    
    if not top_customers.empty:
        st.dataframe(
            top_customers.style.format({
                'TOTAL_SPENT': '€{:,.2f}',
                'ORDER_COUNT': '{:,.0f}',
                'TOTAL_ITEMS': '{:,.0f}'
            }),
            use_container_width=True
        )
    else:
        st.info("Aucune donnée disponible")

st.markdown("---")

# ============================================
# INVENTAIRE
# ============================================
st.header("📦 Gestion de l'Inventaire")

col1, col2 = st.columns(2)

with col1:
    st.subheader("⚠️ Alertes Stock Faible (< 50 unités)")
    low_stock = session.sql("""
        SELECT 
            PRODUCT_ID,
            PRODUCT_NAME,
            PRODUCT_CATEGORY,
            CURRENT_STOCK_LEVEL,
            WAREHOUSE_LOCATION,
            LAST_ADJUSTMENT_TIMESTAMP
        FROM PRODUCTION.INVENTORY_CURRENT
        WHERE CURRENT_STOCK_LEVEL < 50
        ORDER BY CURRENT_STOCK_LEVEL ASC
        LIMIT 15
    """).to_pandas()
    
    if not low_stock.empty:
        st.warning(f"⚠️ {len(low_stock)} produits avec stock critique !")
        st.dataframe(
            low_stock.style.format({
                'CURRENT_STOCK_LEVEL': '{:,.0f}'
            }).background_gradient(subset=['CURRENT_STOCK_LEVEL'], cmap='RdYlGn'),
            use_container_width=True
        )
    else:
        st.success("✅ Tous les stocks sont suffisants")

with col2:
    st.subheader("📊 Répartition du Stock par Catégorie")
    stock_by_category = session.sql("""
        SELECT 
            PRODUCT_CATEGORY,
            COUNT(DISTINCT PRODUCT_ID) AS PRODUCT_COUNT,
            SUM(CURRENT_STOCK_LEVEL) AS TOTAL_STOCK,
            ROUND(AVG(CURRENT_STOCK_LEVEL), 0) AS AVG_STOCK
        FROM PRODUCTION.INVENTORY_CURRENT
        GROUP BY PRODUCT_CATEGORY
        ORDER BY TOTAL_STOCK DESC
    """).to_pandas()
    
    if not stock_by_category.empty:
        st.bar_chart(
            stock_by_category.set_index('PRODUCT_CATEGORY')['TOTAL_STOCK'],
            use_container_width=True
        )
        st.dataframe(
            stock_by_category.style.format({
                'TOTAL_STOCK': '{:,.0f}',
                'AVG_STOCK': '{:,.0f}',
                'PRODUCT_COUNT': '{:,.0f}'
            }),
            use_container_width=True
        )
    else:
        st.info("Aucune donnée d'inventaire disponible")

st.markdown("---")

# ============================================
# MOUVEMENTS D'INVENTAIRE RÉCENTS
# ============================================
st.header("🔄 Mouvements d'Inventaire Récents")

recent_movements = session.sql(f"""
    SELECT 
        ADJUSTMENT_DATE,
        PRODUCT_NAME,
        PRODUCT_CATEGORY,
        ADJUSTMENT_TYPE,
        QUANTITY_CHANGE,
        WAREHOUSE_LOCATION,
        REASON
    FROM PRODUCTION.INVENTORY_HISTORY
    WHERE ADJUSTMENT_TIMESTAMP >= {time_filter}
    ORDER BY ADJUSTMENT_DATE DESC
    LIMIT 20
""").to_pandas()

if not recent_movements.empty:
    st.dataframe(
        recent_movements.style.format({
            'QUANTITY_CHANGE': '{:+,.0f}'
        }),
        use_container_width=True
    )
else:
    st.info("Aucun mouvement récent")

# ============================================
# FOOTER
# ============================================
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.caption("🍷 **Les Caves d'Albert**")
    st.caption("Dashboard BI en temps réel")

with col2:
    st.caption("⚡ Powered by **Snowflake + Streamlit**")
    st.caption("Données mises à jour en temps réel")

with col3:
    st.caption(f"📊 Période analysée: **{time_range}**")
    if selected_categories:
        st.caption(f"🏷️ Catégories: {len(selected_categories)} sélectionnée(s)")
