# 📊 Streamlit Dashboard

Real-time Business Intelligence dashboard for **Les Caves d'Albert** wine shop.

## 📁 Files

```
streamlit/
└── dashboard.py    # Main Streamlit BI dashboard
```

## ✨ Features

- **5 Key Performance Indicators**
  - 🛒 Total Orders
  - 👥 Unique Customers
  - 💰 Total Revenue
  - 🧾 Average Basket Value
  - 📦 Items Sold

- **Interactive Visualizations**
  - 🍷 Top 10 Best-Selling Wines
  - 📊 Sales by Category (Red, White, Sparkling, Spirits)
  - 📅 Revenue Evolution Over Time
  - 👥 Top 10 Customers by Revenue

- **Inventory Management**
  - ⚠️ Low Stock Alerts (< 50 units)
  - 📊 Stock Distribution by Category
  - 🔄 Recent Inventory Movements

- **Filters**
  - 📅 Time Period (24h / 7d / 30d / All time)
  - 🏷️ Product Categories (multi-select)

## 🚀 Deployment

### Option 1: Streamlit in Snowflake (Recommended)

1. Open Snowflake UI → **Streamlit**
2. Click **+ Streamlit App**
3. Configure:
   - **Name**: `Les_Caves_Albert_Dashboard`
   - **Warehouse**: `COMPUTE_WH`
   - **Database**: `CAVES_ALBERT_DB`
4. Copy content from `dashboard.py`
5. Click **Run**

### Option 2: Local Development

```bash
# Install dependencies
pip install streamlit pandas snowflake-snowpark-python

# Run locally (requires Snowflake connection)
streamlit run dashboard.py
```

## 📖 Documentation

- [STREAMLIT_DASHBOARD_GUIDE.md](../documentation/STREAMLIT_DASHBOARD_GUIDE.md) - Complete deployment guide
- [STREAMLIT_LOCAL_README.md](../documentation/STREAMLIT_LOCAL_README.md) - Local setup

## 🎨 Customization

### Change Stock Alert Threshold
```python
# Line ~290 in dashboard.py
WHERE CURRENT_STOCK_LEVEL < 50  # Change this value
```

### Add Custom Time Period
```python
time_mapping = {
    "Last 24 hours": "DATEADD('day', -1, CURRENT_TIMESTAMP())",
    "Last 90 days": "DATEADD('day', -90, CURRENT_TIMESTAMP())",  # Add this
    # ...
}
```

## 📸 Screenshot

The dashboard includes:
- Clean, professional UI with gradient header
- Responsive layout (wide mode)
- Color-coded metrics
- Interactive filters in sidebar
- Real-time data refresh

---

**🍷 Les Caves d'Albert** - Streamlit BI Dashboard
