from ..spark.loader import load_combined_from_parquet
from ..spark.spark_session import get_spark_session
from ..helpers.logger import Logger
import pyspark.sql.functions as F
import pyspark
import os 

logger = Logger("TestLoader")

base_name = "test02_config"
spark = get_spark_session("HHSim Analysis")
in_root = os.path.abspath(os.path.join(os.getcwd(), "python","outputs", "parquet"))
rel_path = os.path.relpath(in_root, os.getcwd())

logger.warn(f'Testing load_combined_from_parquet for {base_name}')
df_loaded = load_combined_from_parquet(spark, 
                                       base_name, 
                                       input_root=in_root)
logger.log(f"Loaded {df_loaded.count()} rows from Parquet: {rel_path}", bSuccess=True)
# df_loaded.show(truncate=False)
df_loaded = None
if df_loaded: 
    df_summary = (
        df_loaded
        .select(
            "sim_id",
            "dt",
            pyspark.sql.functions.size("V").alias("len_V"),
            pyspark.sql.functions.size("spike_windows").alias("N spikes")
        )
        .orderBy("sim_id")
    )
    logger.log(f"[Summary view for {base_name}]")
    df_summary.show(truncate=False)
else: 
    logger.error(f"No data loaded for {base_name}")
