from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, avg
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType

# 1. Initialize Spark Session with Kafka support
spark = SparkSession.builder \
    .appName("CryptoStreamProcessor") \
    .getOrCreate()

# Reduce logging noise
spark.sparkContext.setLogLevel("WARN")

# 2. Define the Schema (matches our Producer's JSON)
schema = StructType([
    StructField("trade_id", StringType(), True),
    StructField("product_id", StringType(), True),
    StructField("price", DoubleType(), True),
    StructField("size", DoubleType(), True),
    StructField("side", StringType(), True),
    StructField("time", TimestampType(), True)
])

# 3. Read from Kafka
# Note: Inside Docker, we use 'kafka:29092' to talk to the broker
raw_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:29092") \
    .option("subscribe", "raw_crypto_trades") \
    .option("startingOffsets", "latest") \
    .load()

# 4. Parse the JSON and Apply Schema
# Kafka sends data as a binary 'value', so we cast it to string first
trades_df = raw_df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

# 5. Real-Time Analytics: 30-Second Moving Average

agg_df = trades_df \
    .withWatermark("time", "10 minutes") \
    .groupBy(
        window(col("time"), "30 seconds"), 
        col("product_id")
    ) \
    .agg(avg("price").alias("average_price"))

# 6. Output to Console (For Verification)
query = agg_df.writeStream \
    .outputMode("complete") \
    .format("console") \
    .option("truncate", "false") \
    .start()

query.awaitTermination()