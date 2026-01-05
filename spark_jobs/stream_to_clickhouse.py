from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType

# Initialize Spark
spark = SparkSession.builder \
    .appName("CryptoClickhouseSink") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

schema = StructType([
    StructField("trade_id", StringType(), True),
    StructField("product_id", StringType(), True),
    StructField("price", DoubleType(), True),
    StructField("size", DoubleType(), True),
    StructField("side", StringType(), True),
    StructField("time", TimestampType(), True)
])

# Read from Kafka
raw_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:29092") \
    .option("subscribe", "raw_crypto_trades") \
    .load()

trades_df = raw_df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

# Aggregate
agg_df = trades_df \
    .withWatermark("time", "10 minutes") \
    .groupBy(window(col("time"), "30 seconds"), col("product_id")) \
    .agg({"price": "avg"}) \
    .select(
        col("window.start").alias("window_start"),
        col("window.end").alias("window_end"),
        col("product_id"),
        col("avg(price)").alias("average_price")
    )

# Function to write each micro-batch to ClickHouse
def write_to_clickhouse(df, epoch_id):
    df.write \
        .format("jdbc") \
        .option("url", "jdbc:clickhouse://clickhouse:8123/default") \
        .option("dbtable", "btc_averages") \
        .option("user", "default") \
        .option("password", "password123") \
        .option("driver", "ru.yandex.clickhouse.ClickHouseDriver") \
        .mode("append") \
        .save()
# Start the stream
query = agg_df.writeStream \
    .foreachBatch(write_to_clickhouse) \
    .outputMode("update") \
    .start()

query.awaitTermination()