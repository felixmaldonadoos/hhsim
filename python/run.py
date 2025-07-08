# run.py - Executes simulations and optionally processes output with Spark

import os
import json

# my custom modules 
from config.confighandler import ConfigHandler
from model import Model
from modelparams import ModelParams
from experimentdata import SimData, ExperimentData
from helpers.progessbar import ProgressBar
from helpers.logger import Logger

# Spark components
import pyspark
from spark.spark_session import get_spark_session
from spark.loader import load_flat_sim_params, load_flat_sim_data, save_combined_as_parquet, load_combined_from_parquet
from spark.transformer import filter_by_param
from spark.analysis import SparkAnalysis
from pyspark.sql import functions as F
from pyspark.sql.types import ArrayType, StructType, StructField, IntegerType

logger = Logger("HHSim")

def run_simulation(params, sim_id):
    # print(f"Running simulation: {sim_id}")
    model = Model(params.to_dict())

    duration = params.duration
    dt = params.dt
    I_ext = params.I_ext
    num_steps = int(duration / dt)

    time_series = []
    voltage_series = []

    time = 0.0
    for _ in range(num_steps):
        model.step(dt, I_ext)
        time_series.append(time)
        voltage_series.append(model.V)
        time += dt

    return time_series, voltage_series

if __name__ == "__main__":
    config_path = "config/tests"
    handler = ConfigHandler()
    handler.load_all_configs(config_path)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "outputs", "traces")
    os.makedirs(output_dir, exist_ok=True)

    experiments = {}
    
    pb = ProgressBar(total=len(handler.configs.items()), prefix="Running simulations")
    for i, (sim_id, config) in enumerate(handler.configs.items()):
        pb.update(i, label=f"Running {sim_id}")

        params = ModelParams(config)
        time, voltage = run_simulation(params, sim_id)

        sim_data = SimData(sim_id, params.to_dict(), time, voltage)
        source_file = config.get("_source_file", "unknown_config.json")

        if source_file not in experiments:
            experiments[source_file] = ExperimentData(source_file)

        experiments[source_file].add_sim(sim_data)

    pb.finish()
    
    for source_file, experiment in experiments.items():
        base_name = os.path.splitext(source_file)[0]
        output_file = os.path.join(output_dir, f"{base_name}_results.json")
        with open(output_file, "w") as f:
            json.dump(experiment.to_dict(), f, indent=2)

        logger.log(f"Saved grouped results → {output_file}")

    # Optional Spark postprocessing example
    spark = get_spark_session("HHSim Analysis")
    for source_file in experiments:
        base_name = os.path.splitext(source_file)[0]
        result_file = os.path.join(output_dir, f"{base_name}_results.json")
        
        ## show params summary stats
        # df = load_flat_sim_params(spark, result_file)
        # print(f"\n[High g_Na sims from {base_name}]")
        # high_gNa = filter_by_param(df, "g_Na", 150)
        # high_gNa.show()
        
        ## get spikes 
        df_data = load_flat_sim_data(spark, result_file)
        df_spikes = SparkAnalysis.detect_spikes_sparkdf(spark,df_data)
        # df_spikes.show()
        
        df_spike_counts = (
            df_data
            .select("sim_id")
            .join(
                df_spikes.groupBy("sim_id").count().withColumnRenamed("count", "num_spikes"),
                on="sim_id",
                how="left"
            )
            .fillna(0, subset=["num_spikes"])
            .orderBy("sim_id")
        )
        
        # group spike windows per sim_id
        df_spike_windows = (
            df_spikes
            .groupBy("sim_id")
            .agg(F.collect_list(F.struct("spike_start", "spike_end")).alias("spike_windows"))
        )
        
        df_combined = df_data.join(df_spike_windows, on="sim_id", how="left")

        # fill nans (sims with no spikes)
        empty_struct = F.struct(
            F.lit(None).cast(IntegerType()).alias("spike_start"),
            F.lit(None).cast(IntegerType()).alias("spike_end")
        )
        
        empty_array_literal = F.expr("array()").cast(ArrayType(StructType([
            StructField("spike_start", IntegerType(), True),
            StructField("spike_end", IntegerType(), True)
        ])))
        
        df_combined = df_combined.withColumn(
            "spike_windows",
            F.when(F.col("spike_windows").isNull(), empty_array_literal).otherwise(F.col("spike_windows"))
        )
        
        params_struct = df_combined.select("params").schema["params"].dataType
        param_cols = [F.col("params." + field.name).alias(field.name) for field in params_struct.fields]

        df_combined = df_combined.select("sim_id", "V", "time", "spike_windows", "params", *param_cols)
        
        logger.log(f"\n[Combined data with spikes for {base_name}]")
        logger.log("Columns:", df_combined.columns)
        
        df_summary = (
            df_combined
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
        
        output_file = save_combined_as_parquet(df_combined, base_name, output_root="outputs/parquet")
        logger.log(f"Saved combined data to Parquet: {output_file}",bSuccess=True)
        # df_combined.show(truncate=False)
        

        logger.warn(f'Testing load_combined_from_parquet for {base_name}')
        df_loaded = load_combined_from_parquet(spark, output_file.split("/")[-1].replace("_combined", ""))
        logger.log(f"Loaded {df_loaded.count()} rows from Parquet: {output_file}", bSuccess=True)
        # df_loaded.show(truncate=False)
        
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