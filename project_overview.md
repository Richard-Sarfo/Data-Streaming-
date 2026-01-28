# Project Overview: Real-Time E-Commerce Data Pipeline

## System Overview

This project implements a real-time data pipeline that simulates an e-commerce platform's user activity tracking system. The pipeline generates synthetic user events, processes them using Apache Spark Structured Streaming, and stores the results in PostgreSQL for analysis.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Data Generator │────▶│  Spark Streaming│────▶│   PostgreSQL    │
│  (Python)       │     │  (Processing)   │     │   (Storage)     │
│                 │     │                 │     │                 │
│ Generates CSV   │     │ Reads CSVs      │     │ streaming.events│
│ event files     │     │ Transforms data │     │ streaming.purchases│
│                 │     │ Writes to DB    │     │ streaming.stats │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Components

### 1. Data Generator (`data_generator.py`)
- Generates fake e-commerce events using the Faker library
- Creates CSV files with user activities: views, add_to_cart, purchases, etc.
- Configurable batch size and generation interval
- Simulates realistic user behavior patterns

### 2. Spark Streaming Processor (`spark_streaming_to_postgres.py`)
- Monitors CSV directory for new files
- Applies data transformations (timestamps, type casting, validation)
- Writes to multiple PostgreSQL tables in parallel:
  - `streaming.events` - All events
  - `streaming.purchases` - Filtered purchase events
  - `streaming.event_stats_hourly` - Aggregated hourly statistics

### 3. PostgreSQL Database (`postgres_setup.sql`)
- Schema: `streaming`
- Tables for events, purchases, hourly stats, and audit logs
- Optimized with indexes for common query patterns

## Data Flow

1. **Generation**: Python script creates CSV files with event data
2. **Ingestion**: Spark detects new files in the monitored directory
3. **Transformation**: Data is cleaned, validated, and enriched
4. **Storage**: Processed data is written to PostgreSQL tables
5. **Analysis**: Data is available for real-time querying and dashboards

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Data Generation | Python + Faker | Create synthetic event data |
| Stream Processing | Apache Spark 4.0 | Real-time data transformation |
| Database | PostgreSQL 14 | Persistent data storage |
| Containerization | Docker Compose | Service orchestration |
| JDBC Driver | PostgreSQL 42.7.1 | Spark-to-PostgreSQL connectivity |

## Event Schema

| Field | Type | Description |
|-------|------|-------------|
| user_id | String | Unique user identifier |
| event_type | String | view, add_to_cart, purchase, etc. |
| product_id | String | Product identifier |
| product_category | String | Electronics, Clothing, Books, etc. |
| product_price | Double | Unit price |
| quantity | Integer | Number of items |
| timestamp | Timestamp | Event occurrence time |
| session_id | UUID | User session identifier |
| device | String | mobile, desktop, tablet |
| country | String | Country code |
| total_amount | Double | Transaction total |
