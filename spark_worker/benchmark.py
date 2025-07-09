from pyspark.sql import SparkSession
import time

def run_benchmark(name, master_url):
    spark = SparkSession.builder \
        .appName(name) \
        .master(master_url) \
        .config("spark.driver.memory", "4g") \
        .getOrCreate() \

    start = time.time()

    df = spark.range(0, 1_000_000)

    df = df.withColumn("squared", df["id"] * df["id"])
    result = df.agg({"squared": "avg"}).collect()

    end = time.time()
    print(f"{name} -> result: {result[0]}, time: {end - start:.2f} seconds")

    spark.stop()

# Run in local mode (all local threads)
run_benchmark("LOCAL[*]", "local[*]")

# Run in cluster mode (submit to master and use workers)
run_benchmark("SPARK CLUSTER", "spark://172.30.127.68:7077")
