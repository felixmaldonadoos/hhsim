from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("WorkerTestJob") \
    .master("spark://172.30.127.68:7077") \
    .getOrCreate()

# Generate a distributed DataFrame
df = spark.range(0, 1000000)
df = df.withColumn("squared", df["id"] * df["id"])

# Trigger some computation
print(df.agg({"squared": "avg"}).collect())

spark.stop()
