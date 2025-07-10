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

    connmanager = connection.PostgresConnectionManager(config)
    conn, cursor = connmanager.connect()

    cursor.execute("""DROP TABLE IF EXISTS simulation_configs""")
    
    cursor.execute("""CREATE TABLE simulation_configs (
        id SERIAL PRIMARY KEY,
        sim_id TEXT UNIQUE,
        C_m FLOAT,
        g_Na FLOAT,
        g_K FLOAT,
        g_L FLOAT,
        E_Na FLOAT,
        E_K FLOAT,
        E_L FLOAT,
        I_ext FLOAT,
        duration FLOAT,
        dt FLOAT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
    """)
    
    data_manager.upload_configs(params_list, conn)
    
    configs_from_db = data_manager.get_configs_from_db(conn)
    connmanager.close()
    

# conn.commit()
# connmanager.close()
