# 📊 SQL Scripts

This directory contains all SQL scripts for the project.

## 📁 Structure

```
sql/
└── snowflake/
    ├── snowflake-tasks-streams.sql    # Main automation pipeline
    └── analytical-queries.sql         # 50+ analytics queries
```

## 🎯 Snowflake Scripts

### `snowflake/snowflake-tasks-streams.sql`
**Main automation pipeline** - Creates the complete ELT pipeline:
- ✅ 5 tables (RAW → STAGING → PRODUCTION)
- ✅ 4 streams (CDC - Change Data Capture)
- ✅ 5 tasks (automated data transformation)

**Usage:**
```sql
-- Execute in Snowflake UI
USE DATABASE CAVES_ALBERT_DB;
USE SCHEMA RAW_DATA;

-- Run the entire script
@snowflake-tasks-streams.sql
```

### `snowflake/analytical-queries.sql`
**50+ analytical queries** for business intelligence:
- Sales analysis by category
- Top customers and products
- Inventory management
- Revenue trends
- Stock alerts

**Usage:**
```sql
-- Execute queries individually in Snowflake
-- Each query is documented with comments
```

## 🔗 Related Documentation

- [SNOWFLAKE_AUTOMATION_GUIDE.md](../documentation/SNOWFLAKE_AUTOMATION_GUIDE.md) - Complete guide
- [SNOWFLAKE_TASKS_README.md](../documentation/SNOWFLAKE_TASKS_README.md) - Task reference

---

**🍷 Les Caves d'Albert** - SQL Scripts
