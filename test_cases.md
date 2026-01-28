# Test Cases: Real-Time Data Pipeline

## Test Plan Overview

This document outlines manual test cases to verify the functionality of the real-time e-commerce data pipeline.

---

## TC-01: CSV File Generation

| Field | Description |
|-------|-------------|
| **Objective** | Verify that data generator creates valid CSV files |
| **Prerequisites** | Docker containers running |
| **Steps** | 1. Run `python data_generator.py --single`<br>2. Check `./csv_data/events/` for new CSV file<br>3. Open CSV and verify content |
| **Expected** | CSV file created with header row and 100 event records |
| **Actual** | |
| **Status** | ⬜ Pass / ⬜ Fail |

---

## TC-02: CSV Schema Validation

| Field | Description |
|-------|-------------|
| **Objective** | Verify CSV files have correct columns and data types |
| **Prerequisites** | At least one CSV file generated |
| **Steps** | 1. Open a generated CSV file<br>2. Verify columns: user_id, event_type, product_id, product_category, product_price, quantity, timestamp, session_id, device, country, total_amount |
| **Expected** | All 11 columns present with valid data |
| **Actual** | |
| **Status** | ⬜ Pass / ⬜ Fail |

---

## TC-03: Spark Stream Detection

| Field | Description |
|-------|-------------|
| **Objective** | Verify Spark detects and processes new CSV files |
| **Prerequisites** | Spark job running, empty events directory |
| **Steps** | 1. Start Spark streaming job<br>2. Generate a new CSV file<br>3. Check Spark logs for file detection |
| **Expected** | Spark logs show file being read and processed |
| **Actual** | |
| **Status** | ⬜ Pass / ⬜ Fail |

---

## TC-04: PostgreSQL Connection

| Field | Description |
|-------|-------------|
| **Objective** | Verify Spark can connect to PostgreSQL |
| **Prerequisites** | PostgreSQL container running |
| **Steps** | 1. Start Spark streaming job<br>2. Check logs for connection success<br>3. Verify no JDBC errors |
| **Expected** | No connection errors in Spark logs |
| **Actual** | |
| **Status** | ⬜ Pass / ⬜ Fail |

---

## TC-05: Events Table Insert

| Field | Description |
|-------|-------------|
| **Objective** | Verify events are inserted into streaming.events table |
| **Prerequisites** | Pipeline running with generated data |
| **Steps** | 1. Process at least one CSV batch<br>2. Query: `SELECT COUNT(*) FROM streaming.events;`<br>3. Verify record count matches CSV rows |
| **Expected** | Record count equals number of events in processed CSVs |
| **Actual** | |
| **Status** | ⬜ Pass / ⬜ Fail |

---

## TC-06: Purchases Table Filter

| Field | Description |
|-------|-------------|
| **Objective** | Verify only purchase events go to streaming.purchases |
| **Prerequisites** | Pipeline running with mixed event types |
| **Steps** | 1. Process CSV with various event types<br>2. Query: `SELECT DISTINCT event_type FROM streaming.events;`<br>3. Query: `SELECT COUNT(*) FROM streaming.purchases;`<br>4. Compare with purchase events in source CSV |
| **Expected** | Purchases table contains only purchase-type events |
| **Actual** | |
| **Status** | ⬜ Pass / ⬜ Fail |

---

## TC-07: Data Transformation - Timestamp

| Field | Description |
|-------|-------------|
| **Objective** | Verify timestamp strings are converted to PostgreSQL timestamp |
| **Prerequisites** | Data inserted into streaming.events |
| **Steps** | 1. Query: `SELECT timestamp, created_at FROM streaming.events LIMIT 5;`<br>2. Verify timestamp is valid PostgreSQL timestamp type |
| **Expected** | Timestamps display correctly as PostgreSQL timestamp format |
| **Actual** | |
| **Status** | ⬜ Pass / ⬜ Fail |

---

## TC-08: Null Value Filtering

| Field | Description |
|-------|-------------|
| **Objective** | Verify rows with null critical fields are filtered out |
| **Prerequisites** | Pipeline running |
| **Steps** | 1. Query: `SELECT * FROM streaming.events WHERE user_id IS NULL OR event_type IS NULL OR product_id IS NULL OR timestamp IS NULL;` |
| **Expected** | Query returns 0 rows |
| **Actual** | |
| **Status** | ⬜ Pass / ⬜ Fail |

---

## TC-09: Hourly Stats Aggregation

| Field | Description |
|-------|-------------|
| **Objective** | Verify hourly statistics are calculated correctly |
| **Prerequisites** | Multiple batches processed |
| **Steps** | 1. Query: `SELECT * FROM streaming.event_stats_hourly ORDER BY hour DESC LIMIT 10;`<br>2. Verify event_count, total_revenue columns have values |
| **Expected** | Aggregated statistics appear with correct calculations |
| **Actual** | |
| **Status** | ⬜ Pass / ⬜ Fail |

---

## TC-10: Continuous Processing

| Field | Description |
|-------|-------------|
| **Objective** | Verify pipeline handles continuous data arrival |
| **Prerequisites** | Pipeline running |
| **Steps** | 1. Start continuous data generation: `python data_generator.py --num-batches 5 --delay 10`<br>2. Monitor Spark job processing each batch<br>3. Verify PostgreSQL records increase with each batch |
| **Expected** | All 5 batches processed without errors |
| **Actual** | |
| **Status** | ⬜ Pass / ⬜ Fail |

---

## Test Summary

| Test ID | Description | Status |
|---------|-------------|--------|
| TC-01 | CSV File Generation | ⬜ |
| TC-02 | CSV Schema Validation | ⬜ |
| TC-03 | Spark Stream Detection | ⬜ |
| TC-04 | PostgreSQL Connection | ⬜ |
| TC-05 | Events Table Insert | ⬜ |
| TC-06 | Purchases Table Filter | ⬜ |
| TC-07 | Data Transformation | ⬜ |
| TC-08 | Null Value Filtering | ⬜ |
| TC-09 | Hourly Stats Aggregation | ⬜ |
| TC-10 | Continuous Processing | ⬜ |

**Total:** 0/10 Passed
