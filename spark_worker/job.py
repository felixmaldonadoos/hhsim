from pyspark.sql import SparkSession
import os 
SPARK_MASTER_IP   = os.environ.get("SPARK_MASTER_IP")
SPARK_MASTER_PORT = os.environ.get("SPARK_MASTER_PORT")    
spark = SparkSession.builder \
    .appName("WorkerTestJob") \
    .master(f"spark://{SPARK_MASTER_IP}:{SPARK_MASTER_PORT}") \
    .getOrCreate()

# Generate a distributed DataFrame
df = spark.range(0, 1000000)
df = df.withColumn("squared", df["id"] * df["id"])

# Trigger some computation
print(df.agg({"squared": "avg"}).collect())

spark.stop()
