# spark/loader.py
import os
from pyspark.sql.functions import col, explode
from pyspark.sql import DataFrame

import pyspark
def load_flat_sim_params(spark, json_path: str) -> DataFrame:
    df = spark.read.option("multiline", "true").json(json_path)
    sims_struct = df.select("sims.*")
    sim_map = sims_struct.selectExpr(
        "map(" + ", ".join([
            f"'{field.name}', `{field.name}`" for field in sims_struct.schema.fields
        ]) + ") as sims_map"
    )
    exploded = sim_map.select(explode("sims_map").alias("sim_id", "sim_struct"))
    sim_params = exploded.select(
        col("sim_id"),
        col("sim_struct.data.params").alias("params")
    )
    return sim_params.select("sim_id", "params.*")


def load_flat_sim_data(spark, json_path: str) -> DataFrame:
    df = spark.read.option("multiline", "true").json(json_path)
    sims_struct = df.select("sims.*")
    sim_map = sims_struct.selectExpr(
        "map(" + ", ".join([
            f"'{field.name}', `{field.name}`" for field in sims_struct.schema.fields
        ]) + ") as sims_map"
    )
    exploded = sim_map.select(explode("sims_map").alias("sim_id", "sim_struct"))
    sim_data = exploded.select(
        col("sim_id"),
        col("sim_struct.data").alias("data")
    )
    return sim_data.select("sim_id", "data.*")



def save_combined_as_parquet(df_combined: DataFrame, base_name: str, output_root: str = "outputs/parquet") -> str:
    """
    Save a combined simulation DataFrame as partitioned Parquet by sim_id.

    Args:
        df_combined (DataFrame): The full Spark DataFrame with sim_id, V, time, params, spike_windows, etc.
        base_name (str): Name to prefix the output directory (e.g., 'test02_config').
        output_root (str): Root output directory. Defaults to 'outputs/parquet'.

    Returns:
        str: Full path to the saved Parquet directory.
    """
    output_parquet_dir = os.path.join(output_root, f"{base_name}_combined")

    df_combined.write \
        .mode("overwrite") \
        .partitionBy("sim_id") \
        .parquet(output_parquet_dir)

    print(f"Saved combined data to Parquet: {output_parquet_dir}")
    return output_parquet_dir

def load_combined_from_parquet(spark: pyspark.sql.SparkSession = None, 
                               base_name: str = None, 
                               input_root: str = "outputs/parquet"):
    """
    Load a previously saved combined Parquet DataFrame.

    Args:
        spark (SparkSession): Active Spark session.
        base_name (str): The name prefix used when saving (e.g., 'test02_config').
        input_root (str): Base directory where Parquet files are stored.

    Returns:
        DataFrame: The loaded Spark DataFrame.
    """
    if spark is None:
        raise ValueError("Spark session must be provided to load Parquet data.")
    
    if base_name is None:
        raise ValueError("Base name must be provided to load Parquet data.")
    
    input_path = os.path.join(input_root, f"{base_name}_combined")

    print(f"Loading Parquet from: {input_path}")
    return spark.read.parquet(input_path)
