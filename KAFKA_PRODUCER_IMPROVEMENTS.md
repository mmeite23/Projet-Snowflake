# 🎉 Kafka Producer Improvements - Les Caves d'Albert 🍷

## 📋 Summary of Changes

The `kafka_producer.py` file has been improved to be **100% consistent** with the data generator `Data_generator_faker_docker.ipynb`.

**Language:** All comments and logs are now in **English** for better international collaboration.

---

## ✨ New Features

### 1. **Visual Emojis** 🎨
Each event and log is now accompanied by emojis for better readability:
- 🛒 **ORDER_CREATED**: New customer orders
- 📦 **REPLENISHMENT**: Stock replenishment
- ✏️ **CORRECTION**: Inventory correction
- ❌ **SPOILAGE**: Product breakage/loss
- 🍷 Rouge | 🥂 Blanc | 🌸 Rosé | 🍾 Effervescent | 🥃 Spiritueux

### 2. **Realistic Product Data** 🍾
Events now include **consistent product names**:
```json
{
  "product_id": 1025,
  "product_name": "Syrah 2018 – Grande Cuvée",
  "category": "🍷 Rouge"
}
```

### 3. **Enriched ORDER_CREATED Event** 🛒

**Before:**
```json
{
  "event_type": "ORDER_CREATED",
  "order_line_id": "uuid",
  "customer_id": 42,
  "product_id": 1025,
  "quantity": 2,
  "event_ts": "2025-10-19T...",
  "source_service": "ecom_api",
  "sales_channel": "E-com"
}
```

**After:**
```json
{
  "event_type": "ORDER_CREATED",
  "order_line_id": "uuid",
  "customer_id": 42,
  "product_id": 1025,
  "product_name": "Syrah 2018 – Grande Cuvée",
  "category": "🍷 Rouge",
  "quantity": 2,
  "unit_price": 24.50,
  "total_price": 49.00,
  "discount": 5.20,
  "bottle_size_l": 0.75,
  "sales_channel": "Boutique Paris",
  "event_ts": "2025-10-19T...",
  "source_service": "ecom_api",
  "emoji": "🛒"
}
```

### 4. **Enriched INVENTORY_ADJUSTED Event** 📦

**Before:**
```json
{
  "event_type": "INVENTORY_ADJUSTED",
  "event_id": "uuid",
  "product_id": 1030,
  "quantity_change": 50,
  "event_ts": "2025-10-19T...",
  "source_service": "warehouse_management",
  "adjustment_type": "REPLENISHMENT"
}
```

**After:**
```json
{
  "event_type": "INVENTORY_ADJUSTED",
  "event_id": "uuid",
  "product_id": 1030,
  "product_name": "Chardonnay 2020 – Prestige",
  "category": "🥂 Blanc",
  "quantity_change": 50,
  "adjustment_type": "REPLENISHMENT",
  "warehouse_location": "Entrepôt Lyon",
  "event_ts": "2025-10-19T...",
  "source_service": "warehouse_management",
  "emoji": "📦"
}
```

---

## 🔧 Consistency with Data_generator_faker_docker

### Data Alignment

| Element | Data Generator | Kafka Producer | ✅ Status |
|---------|---------------|----------------|-----------|
| **Product IDs** | 1000-1049 | 1000-1049 | ✅ Consistent |
| **Customer IDs** | 1-150 | 1-150 | ✅ Consistent |
| **Sales Channels** | E-com, Boutique Paris, Lyon, Bordeaux | Identical | ✅ Consistent |
| **Wine Categories** | Rouge, Blanc, Rosé, Effervescent, Spiritueux | Identical + Emojis | ✅ Consistent |
| **Bottle Sizes** | 0.375, 0.5, 0.75, 1.0, 1.5 | Identical | ✅ Consistent |
| **Quantity Distribution** | [1,2,3,6] with weights [0.6,0.25,0.1,0.05] | Identical | ✅ Consistent |
| **Discount Logic** | 25% chance, 0-10€ | Identical | ✅ Consistent |

---

## 📊 Example of Improved Logs

### Production Logs
```
2025-10-19 14:23:45 - INFO - 🔌 Connecting to Kafka at ['redpanda:9092']
2025-10-19 14:23:46 - INFO - 🍷 Les Caves d'Albert Producer started. Generating events...
2025-10-19 14:23:46 - INFO - ================================================================================
2025-10-19 14:23:46 - INFO - 🛒 ORDER_CREATED | Customer #42 | 🍷 Rouge Merlot 2015 – Réserve | Qty: 2 | Price: €45.60 | Channel: E-com
2025-10-19 14:23:47 - INFO - 📦 INVENTORY_ADJUSTED | Product #1025 | 🥂 Blanc Chardonnay 2020 – Prestige | +75 units | Type: REPLENISHMENT | Entrepôt Lyon
2025-10-19 14:23:48 - INFO - 🛒 ORDER_CREATED | Customer #89 | 🍾 Effervescent Champagne 2016 – Grande Cuvée | Qty: 1 | Price: €52.00 | Channel: Boutique Paris
2025-10-19 14:23:49 - INFO - ✏️ INVENTORY_ADJUSTED | Product #1042 | 🥃 Spiritueux Whisky 2010 – Édition Limitée | -8 units | Type: CORRECTION | Cave Centrale
```

---

## 🚀 Usage

### Starting the Producer
```bash
# From the project directory
python kafka_producer.py
```

### Environment Variables (.env)
```bash
KAFKA_TOPIC_NAME=sales_events
KAFKA_BOOTSTRAP_SERVER=redpanda:9092
```

---

## 📦 Data Structure

### Event Types

1. **ORDER_CREATED (70%)**: Customer orders
2. **INVENTORY_ADJUSTED (30%)**: Stock adjustments
   - REPLENISHMENT (60%): Stock replenishment
   - CORRECTION (30%): Inventory correction
   - SPOILAGE (10%): Breakage/Loss

### Product Names
Format: `{Grape} {Year} – {Adjective}`
- Example: "Merlot 2018 – Grande Cuvée"
- Consistency guaranteed by product_id-based seed

### Pricing Logic
Base price per category (consistent with generator):
- 🍷 Rouge: €18 (±30%)
- 🥂 Blanc: €15 (±30%)
- 🌸 Rosé: €12 (±30%)
- 🍾 Effervescent: €30 (±30%)
- 🥃 Spiritueux: €45 (±30%)

---

## 🎯 Benefits of Improvements

1. **Readability**: Emojis and structured logs facilitate monitoring
2. **Consistency**: Data 100% aligned with SQLite/PostgreSQL generator
3. **Traceability**: Each event contains complete information
4. **Realism**: Consistent product names, prices, and quantities
5. **Debugging**: Detailed logs with event counter
6. **International**: All comments and logs in English

---

## 📈 Production Statistics

The producer generates on average:
- **70%** ORDER_CREATED events (orders)
- **30%** INVENTORY_ADJUSTED events (stock)
  - 18% REPLENISHMENT
  - 9% CORRECTION
  - 3% SPOILAGE

Frequency: **1 event every 0.1 to 0.3 seconds**

---

## ✅ Validation Checklist

- [x] Product IDs consistency (1000-1049)
- [x] Customer IDs consistency (1-150)
- [x] Realistic product names with emojis
- [x] Prices calculated by category
- [x] Consistent bottle sizes
- [x] Identical sales channels
- [x] Identical quantity distribution
- [x] Discount logic (25% chance)
- [x] Inventory adjustment types
- [x] Warehouse locations added
- [x] Enriched logs with emojis
- [x] Event counter
- [x] Graceful shutdown with statistics
- [x] All comments and logs in English

---

🍷 **Les Caves d'Albert** - Kafka Producer v2.0 - October 2025
