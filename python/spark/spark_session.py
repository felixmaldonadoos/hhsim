# spark/spark_session.py
import pyspark
import os 
# local[*]
def get_spark_session(app_name="HHSimApp")->pyspark.sql.SparkSession:
    SPARK_MASTER_IP   = os.environ.get("SPARK_MASTER_IP")
    SPARK_MASTER_PORT = os.environ.get("SPARK_MASTER_PORT")    
    return pyspark.sql.SparkSession.builder \
        .appName(app_name) \
        .config("spark.driver.bindAddress", SPARK_MASTER_IP) \
        .master(f"spark://{SPARK_MASTER_IP}:{SPARK_MASTER_PORT}") \
        .getOrCreate()
        # .config("spark.ui.port", "8080") \
        # .config("spark.driver.memory", "4g") \
