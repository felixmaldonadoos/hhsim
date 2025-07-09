# spark/spark_session.py
from pyspark.sql import SparkSession

# local[*]
# spark://172.30.127.68:7077
def get_spark_session(app_name="HHSimApp"):
    return SparkSession.builder \
        .appName(app_name) \
        .master("local[*]") \
        .config("spark.driver.memory", "4g") \
        .getOrCreate()
