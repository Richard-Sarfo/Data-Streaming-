"""
Spark Structured Streaming to PostgreSQL
Real-time data pipeline that reads CSV files from a directory and writes to PostgreSQL
"""

import os
import sys
from datetime import datetime
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, to_timestamp, current_timestamp, md5, concat_ws,
    from_json, schema_of_json, when, count, sum as spark_sum,
    window, desc
)
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, TimestampType
import logging
from pathlib import Path


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SparkStreamingProcessor:
    """Handle Spark Structured Streaming to PostgreSQL"""
    
    def __init__(self, postgres_config, checkpoint_dir="./checkpoints"):
        """
        Initialize the streaming processor
        
        Args:
            postgres_config: Dictionary with db connection details
            checkpoint_dir: Directory for Spark checkpoints
        """
        self.postgres_config = postgres_config
        self.checkpoint_dir = checkpoint_dir
        self.spark = None
        
        # Create checkpoint directory if it doesn't exist
        Path(checkpoint_dir).mkdir(parents=True, exist_ok=True)
    
    def initialize_spark_session(self):
        """Create and configure Spark session"""
        try:
            self.spark = SparkSession.builder \
                .appName("ECommerceStreamingPipeline") \
                .config("spark.sql.streaming.checkpointLocation", self.checkpoint_dir) \
                .config("spark.sql.shuffle.partitions", "4") \
                .config("spark.streaming.kafka.maxRatePerPartition", "10000") \
                .getOrCreate()
            
            self.spark.sparkContext.setLogLevel("WARN")
            logger.info("Spark session initialized")
            return self.spark
        
        except Exception as e:
            logger.error(f"Failed to initialize Spark session: {e}")
            raise
    
    def get_jdbc_url(self):
        """Build JDBC connection URL"""
        host = self.postgres_config.get('host', 'localhost')
        port = self.postgres_config.get('port', 5432)
        database = self.postgres_config.get('database', 'ecommerce_streaming')
        return f"jdbc:postgresql://{host}:{port}/{database}"
    
    def read_csv_stream(self, input_path):
        """
        Read CSV files from directory as a stream
        
        Args:
            input_path: Path to directory containing CSV files
            
        Returns:
            Streaming DataFrame
        """
        try:
            # Define schema for CSV files
            schema = StructType([
                StructField("user_id", StringType(), True),
                StructField("event_type", StringType(), True),
                StructField("product_id", StringType(), True),
                StructField("product_category", StringType(), True),
                StructField("product_price", DoubleType(), True),
                StructField("quantity", IntegerType(), True),
                StructField("timestamp", StringType(), True),
                StructField("session_id", StringType(), True),
                StructField("device", StringType(), True),
                StructField("country", StringType(), True),
                StructField("total_amount", DoubleType(), True)
            ])
            
            df = self.spark.readStream \
                .schema(schema) \
                .option("header", "true") \
                .option("mode", "PERMISSIVE") \
                .option("maxFilesPerTrigger", "1") \
                .csv(input_path)
            
            logger.info(f"Streaming reader configured for path: {input_path}")
            return df
        
        except Exception as e:
            logger.error(f"Failed to create streaming reader: {e}")
            raise
    
    def transform_data(self, df):
        """
        Apply transformations to the data
        
        Args:
            df: Input DataFrame
            
        Returns:
            Transformed DataFrame
        """
        try:
            df = df \
                .withColumn("timestamp", to_timestamp(col("timestamp"))) \
                .withColumn("created_at", current_timestamp()) \
                .withColumn("processed_at", current_timestamp()) \
                .withColumn("product_price", col("product_price").cast(DoubleType())) \
                .withColumn("total_amount", col("total_amount").cast(DoubleType())) \
                .withColumn("quantity", col("quantity").cast(IntegerType()))
            
            # Validate data: remove rows with null critical fields
            df = df.filter(
                col("user_id").isNotNull() &
                col("event_type").isNotNull() &
                col("product_id").isNotNull() &
                col("timestamp").isNotNull()
            )
            
            logger.info("Data transformation completed")
            return df
        
        except Exception as e:
            logger.error(f"Data transformation failed: {e}")
            raise
    
    def _write_batch_to_postgres(self, df, table_name, batch_size="1000"):
        """
        Helper function to write a DataFrame to a PostgreSQL table using JDBC.
        """
        jdbc_url = self.get_jdbc_url()
        # Add stringtype=unspecified to allow PostgreSQL to convert string to UUID
        jdbc_url_with_params = f"{jdbc_url}?stringtype=unspecified"
        
        df.write \
            .format("jdbc") \
            .option("url", jdbc_url_with_params) \
            .option("dbtable", table_name) \
            .option("user", self.postgres_config.get('user', 'postgres')) \
            .option("password", self.postgres_config.get('password', '')) \
            .option("batchSize", batch_size) \
            .option("isolationLevel", "READ_COMMITTED") \
            .mode("append") \
            .save()

    def write_to_postgres(self, df, table_name="streaming.events"):
        """
        Write streaming data to PostgreSQL using foreachBatch.
        
        Args:
            df: Streaming DataFrame
            table_name: Target table name
            
        Returns:
            StreamingQuery object
        """
        try:
            writer_function = lambda batch_df, epoch_id: self._write_batch_to_postgres(
                batch_df, table_name
            )

            query = df.writeStream \
                .foreachBatch(writer_function) \
                .option("checkpointLocation", os.path.join(self.checkpoint_dir, "events")) \
                .start()
            
            logger.info(f"Streaming write initiated to {table_name}")
            return query
        
        except Exception as e:
            logger.error(f"Failed to write to PostgreSQL: {e}")
            raise
    
    def write_purchases_to_postgres(self, df):
        """
        Write filtered purchase events to PostgreSQL using foreachBatch.
        
        Args:
            df: Streaming DataFrame
            
        Returns:
            StreamingQuery object
        """
        try:
            # Filter for purchase events and select/rename columns to match table schema
            purchases_df = df.filter(col("event_type") == "purchase").select(
                col("user_id"),
                col("product_id"),
                col("product_category"),
                col("product_price"),
                col("quantity"),
                col("total_amount"),
                col("timestamp").alias("purchase_timestamp"),
                col("device"),
                col("country"),
                col("session_id")
            )
            
            table_name = "streaming.purchases"
            writer_function = lambda batch_df, epoch_id: self._write_batch_to_postgres(
                batch_df, table_name, batch_size="500"
            )

            query = purchases_df.writeStream \
                .foreachBatch(writer_function) \
                .option("checkpointLocation", os.path.join(self.checkpoint_dir, "purchases")) \
                .start()
            
            logger.info("Purchase events streaming write initiated")
            return query
        
        except Exception as e:
            logger.error(f"Failed to write purchases to PostgreSQL: {e}")
            raise
    
    def write_aggregated_stats(self, df):
        """
        Write hourly aggregated statistics to PostgreSQL using foreachBatch.
        
        NOTE: This uses 'append' mode. For a production system, you would
        need to implement an 'upsert' (update/insert) logic to avoid
        duplicate rows for the same aggregation window. This can be done by
        writing to a temporary table and then using a MERGE SQL statement.
        
        Args:
            df: Streaming DataFrame
            
        Returns:
            StreamingQuery object
        """
        try:
            # Aggregate by hour and event type
            agg_df = df.withWatermark("timestamp", "10 minutes").groupBy(
                window(col("timestamp"), "1 hour"),
                col("event_type"),
                col("product_category")
            ).agg(
                count("*").alias("event_count"),
                spark_sum("total_amount").alias("total_revenue"),
                count(col("user_id")).alias("unique_users"),
                (spark_sum("quantity") / count("*")).alias("average_quantity")
            ).select(
                col("event_type"),
                col("product_category"),
                col("window.start").alias("hour"),
                col("event_count"),
                col("total_revenue"),
                col("unique_users"),
                col("average_quantity"),
                current_timestamp().alias("calculated_at")
            )
            
            table_name = "streaming.event_stats_hourly"
            # In a production scenario, you'd implement upsert logic here
            def upsert_batch(batch_df, epoch_id):
                # For simplicity, we append. A real implementation would be complex.
                # Example: write to temp table, then MERGE.
                self._write_batch_to_postgres(batch_df, table_name, batch_size="100")

            query = agg_df.writeStream \
                .outputMode("update") \
                .foreachBatch(upsert_batch) \
                .option("checkpointLocation", os.path.join(self.checkpoint_dir, "stats")) \
                .start()
            
            logger.info("Aggregated statistics streaming write initiated")
            return query
        
        except Exception as e:
            logger.error(f"Failed to write aggregated stats: {e}")
            raise
    
    def run_pipeline(self, input_path, wait_termination=True, timeout_seconds=None):
        """
        Run the complete streaming pipeline
        
        Args:
            input_path: Path to CSV directory
            wait_termination: Whether to wait for streaming queries to terminate
            timeout_seconds: Timeout for streaming (None = infinite)
        """
        try:
            self.initialize_spark_session()
            
            # Read streaming data
            df = self.read_csv_stream(input_path)
            
            # Transform data
            transformed_df = self.transform_data(df)
            
            # Start writing to different tables
            logger.info("-" * 60)
            logger.info("Starting streaming queries...")
            logger.info("-" * 60)
            
            query_events = self.write_to_postgres(transformed_df)
            query_purchases = self.write_purchases_to_postgres(transformed_df)
            query_stats = self.write_aggregated_stats(transformed_df)
            
            if wait_termination:
                logger.info("Pipeline running. Press Ctrl+C to stop.")
                
                try:
                    query_events.awaitTermination(timeout=timeout_seconds)
                except KeyboardInterrupt:
                    logger.info("Stopping streaming queries...")
                    query_events.stop()
                    query_purchases.stop()
                    query_stats.stop()
                    logger.info("All queries stopped")
            
            return {
                'events': query_events,
                'purchases': query_purchases,
                'stats': query_stats
            }
        
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            raise
        
        finally:
            if self.spark:
                self.spark.stop()


def load_config_from_file(config_file="postgres_connection_details.txt"):
    """
    Load PostgreSQL connection configuration from file
    
    Args:
        config_file: Path to configuration file
        
    Returns:
        Dictionary with configuration
    """
    config = {
        'host': os.environ.get('POSTGRES_HOST', 'localhost'),
        'port': int(os.environ.get('POSTGRES_PORT', 5432)),
        'database': os.environ.get('POSTGRES_DB', 'ecommerce_streaming'),
        'user': os.environ.get('POSTGRES_USER', 'postgres'),
        'password': os.environ.get('POSTGRES_PASSWORD', '')
    }
    
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            config[key.strip().lower()] = value.strip()
            logger.info(f"✓ Configuration loaded from {config_file}")
        except Exception as e:
            logger.warning(f"⚠ Failed to load config file: {e}. Using defaults.")
    
    return config


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Spark Structured Streaming pipeline for e-commerce events"
    )
    parser.add_argument(
        "--input-path",
        default="./data/events",
        help="Path to CSV input directory (default: ./data/events)"
    )
    parser.add_argument(
        "--config-file",
        default="postgres_connection_details.txt",
        help="PostgreSQL configuration file (default: postgres_connection_details.txt)"
    )
    parser.add_argument(
        "--checkpoint-dir",
        default="./checkpoints",
        help="Checkpoint directory (default: ./checkpoints)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=None,
        help="Timeout in seconds (default: infinite)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Spark Structured Streaming Pipeline")
    print("E-Commerce Event Processing")
    print("=" * 60)
    
    # Load configuration
    postgres_config = load_config_from_file(args.config_file)
    
    print(f"PostgreSQL Host: {postgres_config.get('host')}")
    print(f"PostgreSQL Database: {postgres_config.get('database')}")
    print(f"Input Path: {args.input_path}")
    print(f"Checkpoint Dir: {args.checkpoint_dir}")
    print("-" * 60)
    
    # Create processor and run pipeline
    processor = SparkStreamingProcessor(postgres_config, args.checkpoint_dir)
    
    try:
        processor.run_pipeline(
            args.input_path,
            wait_termination=True,
            timeout_seconds=args.timeout
        )
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
