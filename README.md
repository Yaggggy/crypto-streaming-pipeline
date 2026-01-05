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
