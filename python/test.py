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

def run_simulation(params_dict:dict=None):
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
    
    ### start body 
    # cursor.execute("""DROP TABLE IF EXISTS simulation_configs""")
    
    data_manager.generate_params_table(conn) # Create the table if it doesn't exist
    data_manager.upload_configs(params_list, conn) # upload the parameters to the database - will overwrite existing entries
    
    configs_from_db = data_manager.get_configs_from_db(conn) # fetch all configs from the database
    
    data_manager.generate_results_table(conn) # Create the results table if it doesn't exist
    for config in configs_from_db:
        time, voltage = run_simulation(params)
        sim_data = SimData(config["sim_id"], config, time, voltage)      
        data_manager.upload_simulation_result_row(conn=conn, sim_data=sim_data)
    ### end body
    
    ## end 
    connmanager.close() 
    

# conn.commit()
# connmanager.close()
