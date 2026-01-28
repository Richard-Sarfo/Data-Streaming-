# Real-Time E-Commerce Streaming Pipeline User Guide

This guide provides the commands necessary to run the data generator and Spark streaming pipeline within the Docker container.

## 1. Setup & Initialization

Before running the scripts, ensure your Docker containers are up and running.

### Start the Infrastructure
Run the following command in the root directory (where `compose.yml` is located):

```bash
docker-compose up -d
```

### Prepare Scripts
Ensure your Python scripts are accessible inside the container. The `compose.yml` mounts the `./scripts` directory on the host to `/opt/spark/work-dir/scripts` in the container.

*   Move `data_generator.py` to the `./scripts` folder.
*   Move `spark_streaming_to_postgres.py` to the `./scripts` folder.

## 2. Accessing the Spark Container

Open a terminal shell inside the Spark container:

```bash
docker exec -it realtime_spark /bin/bash
```

*All subsequent commands should be run inside this container shell.*

## 3. Install Dependencies

The data generator requires the `faker` library. Install it inside the container:

```bash
pip install faker
```

## 4. Running the Pipeline

It is recommended to run the generator and the processor in separate terminal windows (exec into the container twice) or run the generator in the background.

### Step A: Start the Data Generator

This will generate events and save them to the mounted data volume so they persist on your host machine.

```bash
python /opt/spark/work-dir/scripts/data_generator.py \
  --output-dir /opt/spark/work-dir/data/events \
  --batch-size 100 \
  --delay 2
```

### Step B: Start the Spark Streaming Job

Submit the Spark job using `spark-submit`. We include the PostgreSQL JDBC driver package to allow Spark to write to the database.

```bash
spark-submit \
  --packages org.postgresql:postgresql:42.6.0 \
  /opt/spark/work-dir/scripts/spark_streaming_to_postgres.py \
  --input-path /opt/spark/work-dir/data/events \
  --checkpoint-dir /opt/spark/work-dir/data/checkpoints
```

## 5. Verification

You can verify the data is landing in PostgreSQL by connecting to the database container:

```bash
# Run on your host machine
docker exec -it streaming-postgres psql -U postgres -d ecommerce_streaming
```

Then run SQL queries:
```sql
SELECT count(*) FROM streaming.events;
SELECT * FROM streaming.event_stats_hourly;
```