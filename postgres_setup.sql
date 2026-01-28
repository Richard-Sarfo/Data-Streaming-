-- PostgreSQL Setup for Real-Time E-Commerce Event Pipeline
-- Create database, tables, and indexes for storing streaming data

-- Create database
-- CREATE DATABASE ecommerce_streaming;

-- Connect to the new database
-- \c ecommerce_streaming;

-- Create schema for organizing tables
CREATE SCHEMA IF NOT EXISTS streaming;

-- Main events table to store all incoming events
CREATE TABLE IF NOT EXISTS streaming.events (
    event_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    product_id VARCHAR(100) NOT NULL,
    product_category VARCHAR(50) NOT NULL,
    product_price NUMERIC(10, 2),
    quantity INTEGER,
    timestamp TIMESTAMP NOT NULL,
    session_id UUID,
    device VARCHAR(20),
    country VARCHAR(10),
    total_amount NUMERIC(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Materialized view for event aggregation (hourly statistics)
CREATE TABLE IF NOT EXISTS streaming.event_stats_hourly (
    stats_id SERIAL PRIMARY KEY,
    event_type VARCHAR(50),
    product_category VARCHAR(50),
    hour TIMESTAMP,
    event_count INTEGER,
    total_revenue NUMERIC(12, 2),
    unique_users INTEGER,
    average_quantity NUMERIC(10, 2),
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Purchase events table (filtered view for analytics)
CREATE TABLE IF NOT EXISTS streaming.purchases (
    purchase_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(100) NOT NULL,
    product_category VARCHAR(50) NOT NULL,
    product_price NUMERIC(10, 2),
    quantity INTEGER,
    total_amount NUMERIC(10, 2),
    purchase_timestamp TIMESTAMP NOT NULL,
    device VARCHAR(20),
    country VARCHAR(10),
    session_id UUID,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User activity summary table
CREATE TABLE IF NOT EXISTS streaming.user_activity_summary (
    user_activity_id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) UNIQUE NOT NULL,
    total_events INTEGER DEFAULT 0,
    total_purchases INTEGER DEFAULT 0,
    total_spent NUMERIC(12, 2) DEFAULT 0,
    last_event_timestamp TIMESTAMP,
    first_event_timestamp TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better query performance
CREATE INDEX idx_events_user_id ON streaming.events(user_id);
CREATE INDEX idx_events_event_type ON streaming.events(event_type);
CREATE INDEX idx_events_timestamp ON streaming.events(timestamp);
CREATE INDEX idx_events_product_category ON streaming.events(product_category);
CREATE INDEX idx_events_created_at ON streaming.events(created_at);

CREATE INDEX idx_purchases_user_id ON streaming.purchases(user_id);
CREATE INDEX idx_purchases_timestamp ON streaming.purchases(purchase_timestamp);
CREATE INDEX idx_purchases_product_category ON streaming.purchases(product_category);

CREATE INDEX idx_stats_hourly_hour ON streaming.event_stats_hourly(hour);
CREATE INDEX idx_stats_hourly_event_type ON streaming.event_stats_hourly(event_type);

-- Create audit table to log data ingestion
CREATE TABLE IF NOT EXISTS streaming.data_ingestion_audit (
    audit_id SERIAL PRIMARY KEY,
    batch_id VARCHAR(100),
    file_name VARCHAR(255),
    records_processed INTEGER,
    records_inserted INTEGER,
    processing_start_time TIMESTAMP,
    processing_end_time TIMESTAMP,
    processing_duration_seconds NUMERIC(10, 2),
    status VARCHAR(20),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes on audit table
CREATE INDEX idx_audit_batch_id ON streaming.data_ingestion_audit(batch_id);
CREATE INDEX idx_audit_created_at ON streaming.data_ingestion_audit(created_at);

-- Create role for the streaming application (optional, for security)
-- Uncomment and modify if using role-based access control
-- CREATE ROLE streaming_app WITH LOGIN PASSWORD 'your_secure_password';
-- GRANT USAGE ON SCHEMA streaming TO streaming_app;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA streaming TO streaming_app;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA streaming TO streaming_app;

-- Grant permissions to public (for testing; restrict in production)
GRANT USAGE ON SCHEMA streaming TO PUBLIC;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA streaming TO PUBLIC;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA streaming TO PUBLIC;

-- Display created tables
\dt streaming.*

COMMIT;
