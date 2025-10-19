# 🍷 Deployment Guide - Streamlit Dashboard in Snowflake

## 📋 Overview

This Streamlit dashboard runs **directly in Snowflake** (Streamlit in Snowflake) to analyze real-time data from "Les Caves d'Albert".

### ✨ Features

- 📊 **5 Main KPIs**: Orders, Customers, Revenue, Avg Basket, Items Sold
- 🍷 **Top 10 Best-Selling Wines**
- 📈 **Analysis by Category** (Red, White, Sparkling, Spirits)
- 📅 **Revenue Time Evolution**
- 👥 **Top Customers** by amount spent
- ⚠️ **Stock Alerts** (products < 50 units)
- 🔄 **Recent Inventory Movements**
- 🎛️ **Interactive Filters**: period, categories

---

## 🚀 Deployment in Snowflake

### **Prerequisites**

✅ Snowflake account with **Streamlit in Snowflake** enabled  
✅ `CAVES_ALBERT_DB` database with PRODUCTION data  
✅ Role with access to PRODUCTION.ORDERS and PRODUCTION.INVENTORY_*

---

### **Step 1: Create Streamlit App in Snowflake**

1. **Log in to Snowflake**
2. In the left menu, click on **Streamlit**
3. Click on **+ Streamlit App**
4. Configure:
   - **App name**: `Les_Caves_Albert_Dashboard`
   - **Warehouse**: `COMPUTE_WH`
   - **App location**:
     - Database: `CAVES_ALBERT_DB`
     - Schema: `PUBLIC` or create `DASHBOARDS`

---

### **Step 2: Copy the code**

1. Open the file `streamlit_dashboard_snowflake.py`
2. **Copy ALL content**
3. **Paste** into Snowflake's Streamlit editor
4. Click **Run** (upper right corner)

---

### **Step 3: Verification**

The dashboard should display:

✅ 5 KPI metrics at the top  
✅ Top 10 wines chart  
✅ Sales by category chart  
✅ Revenue evolution over time  
✅ Low stock alerts  

---

## 🎨 Customization

### **Modify Period Filters**

In the sidebar, "Analysis Period" section:

```python
time_mapping = {
    "Last 24 hours": "DATEADD('day', -1, CURRENT_TIMESTAMP())",
    "Last 7 days": "DATEADD('day', -7, CURRENT_TIMESTAMP())",
    "Last 30 days": "DATEADD('day', -30, CURRENT_TIMESTAMP())",
    "All time": "DATEADD('year', -10, CURRENT_TIMESTAMP())"
}
```

Add your own custom periods!

---

### **Modify Stock Alert Thresholds**

Line ~290, change the value of 50:

```python
WHERE CURRENT_STOCK_LEVEL < 50  # ← Change this value
```

---

### **Add a New Chart**

Example: Add a "Sales by Channel" chart (E-commerce, Store, etc.)

```python
st.subheader("📊 Sales by Channel")
channel_sales = session.sql(f"""
    SELECT 
        PAYMENT_METHOD AS CHANNEL,
        COUNT(*) AS ORDERS,
        ROUND(SUM(TOTAL_AMOUNT), 2) AS REVENUE
    FROM PRODUCTION.ORDERS
    WHERE ORDER_TIMESTAMP >= {time_filter}
    GROUP BY PAYMENT_METHOD
    ORDER BY REVENUE DESC
""").to_pandas()

st.bar_chart(channel_sales.set_index('CHANNEL')['REVENUE'])
```

---

## 📊 Usage

### **Available Filters**

1. **Period**: Last 24h / 7d / 30d / All time
2. **Categories**: Red, White, Sparkling, Spirits (multi-select)

### **Refresh Data**

Click the **🔄 Refresh Data** button in the sidebar.

---

## 🔧 Troubleshooting

### **Error: "Table does not exist"**

**Cause**: PRODUCTION tables don't exist or are not accessible

**Solution**:
```sql
-- Verify tables exist
USE DATABASE CAVES_ALBERT_DB;
SELECT COUNT(*) FROM PRODUCTION.ORDERS;
SELECT COUNT(*) FROM PRODUCTION.INVENTORY_CURRENT;
SELECT COUNT(*) FROM PRODUCTION.INVENTORY_HISTORY;
```

---

### **Error: "Cannot get active session"**

**Cause**: Code is not running in Streamlit in Snowflake

**Solution**: Make sure to use **Streamlit in Snowflake** (not local Streamlit)

---

### **Empty Charts**

**Cause**: No data for the selected period

**Solution**:
1. Select "All time"
2. Verify Snowflake tasks have properly propagated the data
3. Execute: `SELECT COUNT(*) FROM PRODUCTION.ORDERS;`

---

## 🎯 Future Improvements

### **Version 2: Advanced Features**

- [ ] 📧 Email alerts for critical stock
- [ ] 🔮 Sales predictions (ML)
- [ ] 📍 Geographic map of warehouses
- [ ] 💰 Margin analysis by product
- [ ] 📊 PDF report exports
- [ ] 🔔 Real-time notifications

### **Widget Examples to Add**

```python
# Widget: Custom date selector
date_range = st.date_input(
    "Select date range",
    value=(datetime.now() - timedelta(days=30), datetime.now())
)

# Widget: Product search
search_product = st.text_input("🔍 Search for a product")

# Widget: CSV Export
if st.button("📥 Download data"):
    csv = top_products.to_csv(index=False)
    st.download_button(
        label="💾 Download CSV",
        data=csv,
        file_name="top_products.csv",
        mime="text/csv"
    )
```

---

## 📱 Dashboard Sharing

### **Option 1: Internal Snowflake Sharing**

1. In Streamlit in Snowflake, click **Share**
2. Select authorized roles/users
3. They will access via their Snowflake account

### **Option 2: Public URL (if available)**

Some Snowflake accounts allow generating a public URL.

---

## 🔗 Resources

- [Streamlit in Snowflake Documentation](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
- [Snowpark Python API](https://docs.snowflake.com/en/developer-guide/snowpark/python/index)
- [Streamlit API Reference](https://docs.streamlit.io/library/api-reference)

---

## ✅ Deployment Checklist

- [ ] CAVES_ALBERT_DB database created
- [ ] PRODUCTION.ORDERS, INVENTORY_CURRENT, INVENTORY_HISTORY tables populated
- [ ] Streamlit in Snowflake enabled on account
- [ ] COMPUTE_WH warehouse available
- [ ] Code copied to Streamlit editor
- [ ] Dashboard displays correctly
- [ ] Filters work
- [ ] Charts display data
- [ ] Dashboard shared with team

---

**🍷 Enjoy your real-time BI dashboard! 🍷**
