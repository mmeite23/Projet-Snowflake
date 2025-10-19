# 🍷 Les Caves d'Albert - BI Dashboard Streamlit in Snowflake

import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session

# Page configuration
st.set_page_config(
    page_title="🍷 Les Caves d'Albert - BI Dashboard",
    page_icon="🍷",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Get active Snowflake session
session = get_active_session()

# ============================================
# CUSTOM CSS STYLES
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
# SIDEBAR - FILTERS
# ============================================
with st.sidebar:
    st.image("https://em-content.zobj.net/thumbs/120/apple/354/wine-glass_1f377.png", width=100)
    st.title("📊 Filters")
    
    # Time period
    time_range = st.selectbox(
        "Analysis Period",
        ["Last 24 hours", "Last 7 days", "Last 30 days", "All time"]
    )
    
    # Period mapping
    time_mapping = {
        "Last 24 hours": "DATEADD('day', -1, CURRENT_TIMESTAMP())",
        "Last 7 days": "DATEADD('day', -7, CURRENT_TIMESTAMP())",
        "Last 30 days": "DATEADD('day', -30, CURRENT_TIMESTAMP())",
        "All time": "DATEADD('year', -10, CURRENT_TIMESTAMP())"
    }
    time_filter = time_mapping[time_range]
    
    # Product category
    categories = session.sql("""
        SELECT DISTINCT PRODUCT_CATEGORY 
        FROM PRODUCTION.ORDERS 
        WHERE PRODUCT_CATEGORY IS NOT NULL
        ORDER BY PRODUCT_CATEGORY
    """).to_pandas()
    
    selected_categories = st.multiselect(
        "Product Categories",
        options=categories['PRODUCT_CATEGORY'].tolist(),
        default=categories['PRODUCT_CATEGORY'].tolist()
    )
    
    st.markdown("---")
    st.markdown("### 🔄 Refresh")
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

# ============================================
# KEY METRICS (KPIs)
# ============================================
st.header("📈 Key Performance Indicators")

# Build category filter
category_filter = "AND PRODUCT_CATEGORY IN (" + ",".join([f"'{cat}'" for cat in selected_categories]) + ")" if selected_categories else ""

# KPIs query
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
        label="🛒 Orders",
        value=f"{int(kpis['TOTAL_ORDERS']):,}",
        delta="Total"
    )

with col2:
    st.metric(
        label="👥 Customers",
        value=f"{int(kpis['TOTAL_CUSTOMERS']):,}",
        delta="Unique"
    )

with col3:
    st.metric(
        label="💰 Revenue",
        value=f"€{kpis['TOTAL_REVENUE']:,.2f}",
        delta=f"Total"
    )

with col4:
    st.metric(
        label="🧾 Avg Basket",
        value=f"€{kpis['AVG_ORDER_VALUE']:,.2f}",
        delta="Per order"
    )

with col5:
    st.metric(
        label="📦 Items Sold",
        value=f"{int(kpis['TOTAL_ITEMS_SOLD']):,}",
        delta="Total"
    )

st.markdown("---")

# ============================================
# CHARTS - ROW 1
# ============================================
st.header("📊 Sales Analysis")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🍷 Top 10 Best-Selling Wines")
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
        st.info("No data available for this period")

with col2:
    st.subheader("📊 Sales by Category")
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
        st.info("No data available")

st.markdown("---")

# ============================================
# CHARTS - ROW 2
# ============================================
st.header("📈 Time Trends")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📅 Revenue Evolution")
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
        st.caption(f"📊 Trend over the last {len(daily_sales)} days")
    else:
        st.info("No data available")

with col2:
    st.subheader("👥 Top 10 Customers (by Revenue)")
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
        st.info("No data available")

st.markdown("---")

# ============================================
# INVENTORY
# ============================================
st.header("📦 Inventory Management")

col1, col2 = st.columns(2)

with col1:
    st.subheader("⚠️ Low Stock Alerts (< 50 units)")
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
        st.warning(f"⚠️ {len(low_stock)} products with critical stock!")
        st.dataframe(
            low_stock.style.format({
                'CURRENT_STOCK_LEVEL': '{:,.0f}'
            }).background_gradient(subset=['CURRENT_STOCK_LEVEL'], cmap='RdYlGn'),
            use_container_width=True
        )
    else:
        st.success("✅ All stock levels are sufficient")

with col2:
    st.subheader("📊 Stock Distribution by Category")
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
        st.info("No inventory data available")

st.markdown("---")

# ============================================
# RECENT INVENTORY MOVEMENTS
# ============================================
st.header("🔄 Recent Inventory Movements")

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
    st.info("No recent movements")

# ============================================
# FOOTER
# ============================================
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.caption("🍷 **Les Caves d'Albert**")
    st.caption("Real-time BI Dashboard")

with col2:
    st.caption("⚡ Powered by **Snowflake + Streamlit**")
    st.caption("Data updated in real-time")

with col3:
    st.caption(f"📊 Analysis period: **{time_range}**")
    if selected_categories:
        st.caption(f"🏷️ Categories: {len(selected_categories)} selected")
