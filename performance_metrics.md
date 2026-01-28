# Performance Metrics Report

## Overview

This document captures performance metrics for the real-time e-commerce data pipeline built with Spark Structured Streaming and PostgreSQL.

---

## Test Environment

| Component | Specification |
|-----------|---------------|
| **Spark Version** | 4.0.1 |
| **PostgreSQL Version** | 14-alpine |
| **Java Version** | 17.0.17 |
| **Docker Engine** | WSL2 Backend |
| **Host OS** | Windows |
| **RAM Allocated** | 1GB (Spark Driver) |

---

## Data Generation Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| Batch Size | 100 events | Default configuration |
| Generation Interval | 5 seconds | Configurable via --delay |
| Events per Minute | ~1,200 | At default settings |
| CSV File Size | ~15-20 KB | Per batch |

---

## Streaming Performance

### Processing Latency

| Metric | Value | Target |
|--------|-------|--------|
| File Detection | < 1 second | ✅ |
| Batch Processing Time | TBD | < 5 seconds |
| End-to-End Latency | TBD | < 10 seconds |

*Note: Fill in actual values after running tests*

### Throughput

| Metric | Value | Notes |
|--------|-------|-------|
| Events per Batch | 100 | Configurable |
| Batches per Minute | ~12 | At 5s interval |
| Records Written/Min | TBD | Measure after testing |

---

## Database Write Performance

### Insert Rates

| Table | Records/Batch | Write Time | Notes |
|-------|---------------|------------|-------|
| streaming.events | 100 | TBD | All events |
| streaming.purchases | ~20 | TBD | ~20% are purchases |
| streaming.event_stats_hourly | Variable | TBD | Aggregated stats |

### JDBC Configuration

| Setting | Value |
|---------|-------|
| Batch Size | 1000 (events), 500 (purchases), 100 (stats) |
| Isolation Level | READ_COMMITTED |
| Connection Pool | Default |

---

## Resource Utilization

### Spark Driver

| Metric | Idle | Under Load |
|--------|------|------------|
| Memory Used | TBD | TBD |
| CPU Usage | TBD | TBD |

### PostgreSQL

| Metric | Value |
|--------|-------|
| Active Connections | TBD |
| Query Response Time | TBD |
| Disk Usage Growth | TBD |

---

## Checkpoint Performance

| Metric | Value |
|--------|-------|
| Checkpoint Directory | ./checkpoints |
| Checkpoint Interval | Per micro-batch |
| Recovery Time | TBD |

---

## Observations & Recommendations

### Current Performance

1. **Strengths**
   - Pipeline successfully processes streaming data
   - JDBC writes work without errors after UUID fix
   - Checkpoint mechanism ensures fault tolerance

2. **Areas for Improvement**
   - Consider increasing batch size for higher throughput
   - Add connection pooling for better database performance
   - Implement rate limiting for backpressure handling

### Tuning Recommendations

| Parameter | Current | Recommended | Impact |
|-----------|---------|-------------|--------|
| spark.sql.shuffle.partitions | 4 | 2-4 | Reduce for small data |
| maxFilesPerTrigger | 1 | 5-10 | Higher throughput |
| JDBC batchSize | 1000 | 2000-5000 | Fewer DB round trips |

---

## How to Collect Metrics

### Measure Processing Time

```sql
-- Check events per minute
SELECT 
    date_trunc('minute', created_at) as minute,
    COUNT(*) as events_count
FROM streaming.events
GROUP BY 1
ORDER BY 1 DESC
LIMIT 10;
```

### Check Spark UI

Access Spark UI at `http://localhost:4040` during job execution to view:
- Streaming tab for micro-batch statistics
- Jobs tab for execution time
- SQL tab for query plans

---

## Test Results Summary

| Test Scenario | Events Processed | Duration | Throughput | Status |
|---------------|------------------|----------|------------|--------|
| Single Batch | 100 | TBD | TBD | ⬜ |
| 5 Batches | 500 | TBD | TBD | ⬜ |
| 10 Batches | 1000 | TBD | TBD | ⬜ |
| Sustained (5 min) | TBD | 5 min | TBD | ⬜ |

---

*Report Generated: [Date]*  
*Last Updated: [Date]*
