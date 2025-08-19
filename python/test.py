# run.py - Executes simulations and optionally processes output with Spark

import os
import json
import numpy as np 

# my custom modules 
from config.confighandler import ConfigHandler
from model import Model
from modelparams import ModelParams
from experimentdata import SimData, ExperimentData
from helpers.progessbar import ProgressBar
from helpers.logger import Logger
import sparql
from postgresql import postgresql_config, connection, data_manager

# Spark components
import pyspark
from spark.spark_session import get_spark_session
from spark.loader import load_flat_sim_params, load_flat_sim_data, save_combined_as_parquet, load_combined_from_parquet
from spark.transformer import filter_by_param
from spark.analysis import SparkAnalysis
from pyspark.sql import functions as F
from pyspark.sql.types import ArrayType, StructType, StructField, IntegerType

logger = Logger("HHSimTEST")
import copy

def run_simulation(params_dict):
    # print(f"Running simulation: {sim_id}")
    # print(type(params_dict))
    params_dict = copy.deepcopy(params_dict)
    # print(params_dict)
    model = Model(params_dict)

    duration = params_dict["duration"]
    dt = params_dict["dt"]
    I_ext = params_dict["I_ext"]
    num_steps = int(duration / dt)

    time_series = []
    voltage_series = []

    time = 0.0
    for _ in range(num_steps):
        model.step(dt, I_ext)
        time_series.append(time)
        voltage_series.append(model.V)
        time += dt

    print(np.mean(voltage_series))
    return time_series, voltage_series

if __name__ == "__main__":
    import time as tm
    t0 = tm.time()
    config_path = "config/tests"
    
    base_dir = os.path.join(os.getcwd(),"python")
    logger.warn((f"Base directory: {base_dir}"))
    
    config_path = os.path.join(base_dir,config_path)
    handler = ConfigHandler()
    handler.load_all_configs(config_path)

    # base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, "outputs", "traces")
    os.makedirs(output_dir, exist_ok=True)

    experiments = {}
    
    pb = ProgressBar(total=len(handler.configs.items()), prefix="Generating Params")
    params_list = []
    for i, (sim_id, config) in enumerate(handler.configs.items()):
        pb.update(i)
        params = ModelParams(config, sim_id=sim_id)
        params_list.append(params.to_dict())
    
    pb.finish()
    config = postgresql_config.PostgresConfig()
    logger.log("PostgresConfig initialized")

    ## start 
    connmanager = connection.PostgresConnectionManager(config)
    conn, cursor = connmanager.connect()


    ## start body
    cursor.execute("""DROP TABLE IF EXISTS simulation_configs CASCADE""")
    cursor.execute("""DROP TABLE IF EXISTS simulation_results CASCADE""")
    conn.commit() # commit the changes to the database
    data_manager.generate_params_table(conn) # Create the table if it doesn't exist
    data_manager.upload_configs(params_list, conn) # upload the parameters to the database - will overwrite existing entries
    configs_from_db = data_manager.get_configs_from_db(conn) # fetch all configs from the database
    data_manager.generate_results_table(conn) # Create the results table if it doesn't exist
    
    # run simulations
    pb = ProgressBar(total=len(configs_from_db), prefix="Running Simulations")
    sim_data_list = []
    for i, config in enumerate(params_list):
        # print(config)
        time, voltage = run_simulation(config)
        sim_data = SimData(config["sim_id"], config, time, voltage)     
        sim_data_list.append(sim_data)
        pb.update(i)    
    pb.finish()
    
    # # upload simulation results to the database
    # pb = ProgressBar(total=len(sim_data_list), prefix="Uploading Results to DB")
    # for i, data in enumerate(sim_data_list):
    #     data_manager.upload_simulation_result_row(conn=conn, sim_data=data)
    #     pb.update(i)
    # pb.finish()
    
    # target_var = "voltage_series"
    # for config in configs_from_db:
    #     simid = config["sim_id"]
    #     d = data_manager.get_simulation_result_by_id(conn, simid, target_var)
    #     logger.log(f"Simulation ID: {simid}, Data: {d[target_var]}")
    #     break
    
    .
    ### LETS GET SPARK GOING
    spark = get_spark_session("HHSim Analysis")
    logger.log("Spark session initialized")
    df = sparql.FileManager.load_postgres_table(spark=spark)
    print(type(df))
    df_transformed = df.withColumn(
        "voltage_series_scaled",
        pyspark.sql.functions.transform(pyspark.sql.functions.col("voltage_series"), lambda x: x ** 4)
    )

    b_exists = sparql.FileManager.table_exists(spark=spark, table_name="simulation_results_transformed")
    if b_exists:
        logger.warn("Table 'simulation_results_transformed' already exists. Skipping creation.")
    else:
        logger.warn("Table 'simulation_results_transformed' does not exist. Creating it.")
        sparql.FileManager.write_df_as_table(spark=spark, df=df_transformed, table_name="simulation_results_transformed")

    logger.log(f"Loaded DataFrame with {df.count()} rows and {len(df.columns)} columns")
    
    ### end body
    
    ## end 
    connmanager.close() 
    