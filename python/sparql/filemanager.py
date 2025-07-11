import os
import pyspark.sql

class FileManager:
    
    @staticmethod
    def load_postgres_table(spark:pyspark.sql.SparkSession=None,
                            table_name: str = "simulation_results")->pyspark.sql.DataFrame:
        if not spark:
            raise ValueError("Spark session is not initialized. Please provide a valid Spark session.")
        
        SQL_IP = os.environ.get("SPARK_POSTGRESQL_IP")
        SQL_PORT = os.environ.get("SPARK_POSTGRESQL_PORT")
        SQL_PW = os.environ.get("SPARK_POSTGRESQL_PW")
        SQL_USER = os.environ.get("SPARK_POSTGRESQL_USER")

        if not all([SQL_IP, SQL_PORT, SQL_PW, SQL_USER]):
            raise EnvironmentError("PostgreSQL credentials are not fully set in environment variables.")
        
        return spark.read \
            .format("jdbc") \
            .option("url", f"jdbc:postgresql://{SQL_IP}:{SQL_PORT}/postgres") \
            .option("dbtable", table_name) \
            .option("user", SQL_USER) \
            .option("password", SQL_PW) \
            .option("driver", "org.postgresql.Driver") \
            .load()
        
    @staticmethod
    def write_df_as_table(spark:pyspark.sql.SparkSession=None, 
                          df:pyspark.sql.DataFrame=None, 
                          table_name:str="default_table")->None:
        df.write \
            .format("jdbc") \
            .option("url", f"jdbc:postgresql://{os.environ['SPARK_POSTGRESQL_IP']}:{os.environ['SPARK_POSTGRESQL_PORT']}/postgres") \
            .option("dbtable", table_name) \
            .option("user", os.environ['SPARK_POSTGRESQL_USER']) \
            .option("password", os.environ['SPARK_POSTGRESQL_PW']) \
            .option("driver", "org.postgresql.Driver") \
            .mode("overwrite") \
            .save()
        return

    @staticmethod
    def table_exists(spark, table_name: str) -> bool:
        """Check if a PostgreSQL table exists via Spark JDBC"""
        SQL_IP = os.environ.get("SPARK_POSTGRESQL_IP")
        SQL_PORT = os.environ.get("SPARK_POSTGRESQL_PORT")
        SQL_USER = os.environ.get("SPARK_POSTGRESQL_USER")
        SQL_PW = os.environ.get("SPARK_POSTGRESQL_PW")

        try:
            result = spark.read \
                .format("jdbc") \
                .option("url", f"jdbc:postgresql://{SQL_IP}:{SQL_PORT}/postgres") \
                .option("dbtable", table_name) \
                .option("user", SQL_USER) \
                .option("password", SQL_PW) \
                .option("driver", "org.postgresql.Driver") \
                .load()
            exists = result.first()[0] is not None
            return exists
        
        except pyspark.sql.utils.AnalysisException:
            return False
        except Exception as e:
            # print(f"[ERR] Unexpected error while checking table existence: {e}")
            return False 
