# spark/spark_session.py
from pyspark.sql import SparkSession

def get_spark_session(app_name="HHSimApp"):
    return SparkSession.builder \
        .appName(app_name) \
        .master("local[*]") \
        .getOrCreate()
