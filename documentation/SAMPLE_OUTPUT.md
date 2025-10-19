# 📊 Sample Output - Kafka Producer - Les Caves d'Albert

## 🎬 Producer Startup

```
2025-10-19 15:30:12 - INFO - 🔌 Connecting to Kafka at ['redpanda:9092']
2025-10-19 15:30:13 - INFO - 🍷 Les Caves d'Albert Producer started. Generating events...
2025-10-19 15:30:13 - INFO - ================================================================================
```

---

## 🛒 Sample ORDER_CREATED Events

```
2025-10-19 15:30:14 - INFO - 🛒 ORDER_CREATED | Customer #23 | 🍷 Rouge Merlot 2015 – Réserve | Qty: 1 | Price: €22.50 | Channel: E-com

2025-10-19 15:30:15 - INFO - 🛒 ORDER_CREATED | Customer #87 | 🥂 Blanc Chardonnay 2020 – Prestige | Qty: 2 | Price: €36.00 | Channel: Boutique Paris

2025-10-19 15:30:16 - INFO - 🛒 ORDER_CREATED | Customer #142 | 🍾 Effervescent Champagne 2018 – Grande Cuvée | Qty: 3 | Price: €105.00 | Channel: Boutique Lyon

2025-10-19 15:30:17 - INFO - 🛒 ORDER_CREATED | Customer #56 | 🌸 Rosé Grenache Rosé 2022 – Tradition | Qty: 1 | Price: €14.75 | Channel: E-com

2025-10-19 15:30:18 - INFO - 🛒 ORDER_CREATED | Customer #134 | 🥃 Spiritueux Whisky 2012 – Édition Limitée | Qty: 1 | Price: €68.50 | Channel: Boutique Bordeaux
```

---

## 📦 Sample INVENTORY_ADJUSTED Events

### Replenishment (Stock Increase)
```
2025-10-19 15:30:19 - INFO - 📦 INVENTORY_ADJUSTED | Product #1015 | 🍷 Rouge Syrah 2017 – Vieilles Vignes | +125 units | Type: REPLENISHMENT | Entrepôt Lyon

2025-10-19 15:30:22 - INFO - 📦 INVENTORY_ADJUSTED | Product #1032 | 🥂 Blanc Sauvignon Blanc 2021 – Sélection | +85 units | Type: REPLENISHMENT | Cave Centrale
```

### Correction (Inventory Adjustment)
```
2025-10-19 15:30:25 - INFO - ✏️ INVENTORY_ADJUSTED | Product #1008 | 🍷 Rouge Pinot Noir 2019 – Prestige | -12 units | Type: CORRECTION | Entrepôt Paris

2025-10-19 15:30:28 - INFO - ✏️ INVENTORY_ADJUSTED | Product #1045 | 🌸 Rosé Cinsault Rosé 2023 – Réserve | -7 units | Type: CORRECTION | Entrepôt Bordeaux
```

### Spoilage (Product Loss)
```
2025-10-19 15:30:31 - INFO - ❌ INVENTORY_ADJUSTED | Product #1027 | 🍾 Effervescent Crémant 2020 – Tradition | -5 units | Type: SPOILAGE | Cave Centrale

2025-10-19 15:30:34 - INFO - ❌ INVENTORY_ADJUSTED | Product #1041 | 🥃 Spiritueux Cognac 2010 – Grande Cuvée | -3 units | Type: SPOILAGE | Entrepôt Lyon
```

---

## 🔄 Mixed Event Stream (Real-time simulation)

```
2025-10-19 15:30:35 - INFO - 🛒 ORDER_CREATED | Customer #98 | 🍷 Rouge Cabernet Sauvignon 2016 – Sélection | Qty: 2 | Price: €42.00 | Channel: E-com
2025-10-19 15:30:36 - INFO - 🛒 ORDER_CREATED | Customer #12 | 🥂 Blanc Riesling 2021 – Tradition | Qty: 1 | Price: €18.50 | Channel: Boutique Paris
2025-10-19 15:30:37 - INFO - 📦 INVENTORY_ADJUSTED | Product #1019 | 🍷 Rouge Malbec 2018 – Réserve | +95 units | Type: REPLENISHMENT | Entrepôt Paris
2025-10-19 15:30:38 - INFO - 🛒 ORDER_CREATED | Customer #67 | 🍾 Effervescent Prosecco 2022 – Prestige | Qty: 6 | Price: €180.00 | Channel: Boutique Lyon
2025-10-19 15:30:39 - INFO - ✏️ INVENTORY_ADJUSTED | Product #1033 | 🥂 Blanc Viognier 2020 – Grande Cuvée | -9 units | Type: CORRECTION | Cave Centrale
2025-10-19 15:30:40 - INFO - 🛒 ORDER_CREATED | Customer #145 | 🌸 Rosé Syrah Rosé 2023 – Édition Limitée | Qty: 1 | Price: €16.25 | Channel: E-com
2025-10-19 15:30:41 - INFO - 🛒 ORDER_CREATED | Customer #29 | 🥃 Spiritueux Rhum 2015 – Vieilles Vignes | Qty: 2 | Price: €92.00 | Channel: Boutique Bordeaux
2025-10-19 15:30:42 - INFO - 🛒 ORDER_CREATED | Customer #81 | 🍷 Rouge Syrah 2019 – Prestige | Qty: 1 | Price: €25.75 | Channel: E-com
2025-10-19 15:30:43 - INFO - 📦 INVENTORY_ADJUSTED | Product #1012 | 🍷 Rouge Merlot 2017 – Grande Cuvée | +110 units | Type: REPLENISHMENT | Entrepôt Lyon
2025-10-19 15:30:44 - INFO - ❌ INVENTORY_ADJUSTED | Product #1038 | 🥂 Blanc Chardonnay 2019 – Tradition | -4 units | Type: SPOILAGE | Entrepôt Bordeaux
```

---

## 🛑 Producer Shutdown

```
^C
2025-10-19 15:35:45 - WARNING - ⚠️  Signal 2 received: shutting down producer...
2025-10-19 15:35:45 - INFO - ================================================================================
2025-10-19 15:35:45 - INFO - 📊 Total events generated: 1247
2025-10-19 15:35:45 - INFO - 🔄 Flushing and closing producer...
2025-10-19 15:35:46 - INFO - 🛑 Producer stopped - Les Caves d'Albert
```

---

## 📋 Event JSON Examples

### ORDER_CREATED Event (Full JSON)
```json
{
  "event_type": "ORDER_CREATED",
  "order_line_id": "a3f7b2c1-4d5e-6f7g-8h9i-0j1k2l3m4n5o",
  "customer_id": 87,
  "product_id": 1025,
  "product_name": "Chardonnay 2020 – Prestige",
  "category": "🥂 Blanc",
  "quantity": 2,
  "unit_price": 18.00,
  "total_price": 36.00,
  "discount": 5.20,
  "bottle_size_l": 0.75,
  "sales_channel": "Boutique Paris",
  "event_ts": "2025-10-19T15:30:15.123456+00:00",
  "source_service": "ecom_api",
  "emoji": "🛒"
}
```

### INVENTORY_ADJUSTED Event - Replenishment (Full JSON)
```json
{
  "event_type": "INVENTORY_ADJUSTED",
  "event_id": "b4g8c3d2-5e6f-7g8h-9i0j-1k2l3m4n5o6p",
  "product_id": 1015,
  "product_name": "Syrah 2017 – Vieilles Vignes",
  "category": "🍷 Rouge",
  "quantity_change": 125,
  "adjustment_type": "REPLENISHMENT",
  "warehouse_location": "Entrepôt Lyon",
  "event_ts": "2025-10-19T15:30:19.789012+00:00",
  "source_service": "warehouse_management",
  "emoji": "📦"
}
```

### INVENTORY_ADJUSTED Event - Correction (Full JSON)
```json
{
  "event_type": "INVENTORY_ADJUSTED",
  "event_id": "c5h9d4e3-6f7g-8h9i-0j1k-2l3m4n5o6p7q",
  "product_id": 1008,
  "product_name": "Pinot Noir 2019 – Prestige",
  "category": "🍷 Rouge",
  "quantity_change": -12,
  "adjustment_type": "CORRECTION",
  "warehouse_location": "Entrepôt Paris",
  "event_ts": "2025-10-19T15:30:25.345678+00:00",
  "source_service": "warehouse_management",
  "emoji": "✏️"
}
```

### INVENTORY_ADJUSTED Event - Spoilage (Full JSON)
```json
{
  "event_type": "INVENTORY_ADJUSTED",
  "event_id": "d6i0e5f4-7g8h-9i0j-1k2l-3m4n5o6p7q8r",
  "product_id": 1027,
  "product_name": "Crémant 2020 – Tradition",
  "category": "🍾 Effervescent",
  "quantity_change": -5,
  "adjustment_type": "SPOILAGE",
  "warehouse_location": "Cave Centrale",
  "event_ts": "2025-10-19T15:30:31.901234+00:00",
  "source_service": "warehouse_management",
  "emoji": "❌"
}
```

---

## 📊 Statistics Summary

### Event Distribution (5 minutes of production)
- **Total Events**: 1,247
- **ORDER_CREATED**: 873 events (70.0%)
- **INVENTORY_ADJUSTED**: 374 events (30.0%)
  - REPLENISHMENT: 224 events (18.0%)
  - CORRECTION: 112 events (9.0%)
  - SPOILAGE: 38 events (3.0%)

### Channel Distribution (Orders only)
- **E-com**: 436 orders (49.9%)
- **Boutique Paris**: 152 orders (17.4%)
- **Boutique Lyon**: 143 orders (16.4%)
- **Boutique Bordeaux**: 142 orders (16.3%)

### Category Distribution (All events)
- **🍷 Rouge**: 398 events (31.9%)
- **🥂 Blanc**: 312 events (25.0%)
- **🌸 Rosé**: 187 events (15.0%)
- **🍾 Effervescent**: 212 events (17.0%)
- **🥃 Spiritueux**: 138 events (11.1%)

### Performance Metrics
- **Average Rate**: 4.16 events/second
- **Peak Rate**: 6.2 events/second
- **Minimum Interval**: 0.1 seconds
- **Maximum Interval**: 0.3 seconds

---

🍷 **Les Caves d'Albert** - Kafka Producer Output - October 2025
