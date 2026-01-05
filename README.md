# Real-Time Cryptocurrency Streaming Pipeline

![Python](https://img.shields.io/badge/Python-3.9-blue?style=for-the-badge&logo=python&logoColor=white)
![Spark](https://img.shields.io/badge/Apache%20Spark-Structured%20Streaming-orange?style=for-the-badge&logo=apachespark&logoColor=white)
![Kafka](https://img.shields.io/badge/Apache%20Kafka-Distributed%20Streaming-black?style=for-the-badge&logo=apachekafka&logoColor=white)
![ClickHouse](https://img.shields.io/badge/ClickHouse-OLAP%20Database-ffcc00?style=for-the-badge&logo=clickhouse&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white)

An end-to-end distributed data engineering pipeline that ingests live Bitcoin trade data, processes it in real-time using **Apache Spark**, and stores aggregated analytics in **ClickHouse** for high-performance querying.

---

## 🏗 Architecture

**Data Flow:** `Coinbase WebSocket` → `Python Producer` → `Apache Kafka` → `Apache Spark` → `ClickHouse`



1.  **Ingestion:** A Python producer connects to the **Coinbase Pro WebSocket API** to receive raw trade data (Ticker: BTC-USD).
2.  **Buffering:** Raw trades are pushed to **Apache Kafka** to handle backpressure and decouple ingestion from processing.
3.  **Processing:** **Apache Spark (Structured Streaming)** reads from Kafka, applying a **30-second Tumbling Window** to calculate the moving average price.
4.  **Storage:** Aggregated results are written to **ClickHouse**, an OLAP database optimized for time-series analytics.
5.  **Infrastructure:** The entire stack is containerized using **Docker Compose** with internal bridging and named volumes.

---

## 🛠 Tech Stack

* **Language:** Python 3.9 (PySpark)
* **Ingestion Source:** Coinbase WebSocket API
* **Message Broker:** Apache Kafka (Confluent Image) & Zookeeper
* **Stream Processing:** Apache Spark 3.5.0 (Structured Streaming)
* **Storage (OLAP):** ClickHouse Server (Latest)
* **Orchestration:** Docker Compose

---

## 📂 Project Structure

```text
├── docker-compose.yml       # Orchestrates Zookeeper, Kafka, Spark, ClickHouse
├── .gitignore               # Ignores sensitive data and logs
├── producer/
│   ├── producer.py          # Script: Fetches data from WebSocket -> Pushes to Kafka
│   └── requirements.txt     # Python dependencies for producer
└── spark_jobs/
    └── stream_to_clickhouse.py  # Script: PySpark Aggregation -> Writes to ClickHouse
```

## How to Run

1. Prerequisites
Docker Desktop installed and running.

Python 3.x installed (for local testing, though the project runs in Docker).

2. Start Infrastructure
Spin up the containerized environment. This creates the network and named volumes.

```text
docker-compose up -d
```
3. Initialize Database

Create the destination table in ClickHouse.



```text
docker exec -it clickhouse clickhouse-client --user default --password password123 --query " CREATE TABLE IF NOT EXISTS btc_averages (
    window_start DateTime,
    window_end DateTime,
    product_id String,
    average_price Float64
) ENGINE = MergeTree()
ORDER BY window_start;"
```


4. Start Data Producer
Run the producer to start streaming live trades into the Kafka topic.

```textpython producer/producer.py```

Expected Log: Delivered to raw_crypto_trades

5. Submit Spark Job
Submit the job to the Spark Master. Note: I use the ru.yandex legacy driver to ensure compatibility with Spark's internal HTTP clients.

```text

docker exec spark spark-submit \
  --packages "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,ru.yandex.clickhouse:clickhouse-jdbc:0.3.2" \
  /app/spark_jobs/stream_to_clickhouse.py
```

6. Verify Results
Watch the aggregated data land in the database in real-time.
```text
docker exec -it clickhouse clickhouse-client --user default --password password123 --query "SELECT * FROM btc_averages ORDER BY window_start DESC LIMIT 10"
```

##Troubleshooting & Challenges Solved
1. "Permission Denied" on Windows/WSL2
Issue: Mounting a local folder to ClickHouse caused filesystem errors (errno 1001).

Solution: Migrated from bind mounts to Docker Named Volumes (clickhouse_storage) to bypass the host filesystem permissions entirely.

2. Dependency Conflict (Class Not Found)
Issue: The official ClickHouse JDBC driver (com.clickhouse) conflicted with Spark's internal HTTP libraries.

Solution: Implemented the Legacy Yandex Driver (ru.yandex.clickhouse:0.3.2) which is stable for Spark 3.x integration.

3. "Transactions Unsupported" Warning
Context: Spark logs warnings about isolation levels.

Resolution: These are expected behaviors for OLAP databases. The pipeline correctly handles this by appending data regardless of transaction support.


Created by Yagyansh 
