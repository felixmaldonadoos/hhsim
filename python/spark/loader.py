# spark/loader.py
import os
from pyspark.sql.functions import col, explode
from pyspark.sql import DataFrame

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

