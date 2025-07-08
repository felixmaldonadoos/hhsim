# run.py - Executes simulations and optionally processes output with Spark

import os
import json
from config.confighandler import ConfigHandler
from model import Model
from modelparams import ModelParams
from experimentdata import SimData, ExperimentData

# Spark components
from spark.spark_session import get_spark_session
from spark.loader import load_flat_sim_params
from spark.transformer import filter_by_param
from spark.analysis import SparkAnalysis
from helpers.progessbar import ProgressBar

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
    
    pb = ProgressBar(total=len(handler.configs.items()), prefix="Running simulations ")
    for i, (sim_id, config) in enumerate(handler.configs.items()):
        pb.update(i, label=f"Running {sim_id}")

        params = ModelParams(config)
        time, voltage = run_simulation(params, sim_id)

        sim_data = SimData(sim_id, params.to_dict(), time, voltage)
        source_file = config.get("_source_file", "unknown_config.json")

        if source_file not in experiments:
            experiments[source_file] = ExperimentData(source_file)

        experiments[source_file].add_sim(sim_data)
        # print(f"Finished simulation: {sim_id} (from {source_file})")

    pb.finish()
    
    for source_file, experiment in experiments.items():
        base_name = os.path.splitext(source_file)[0]
        output_file = os.path.join(output_dir, f"{base_name}_results.json")
        with open(output_file, "w") as f:
            json.dump(experiment.to_dict(), f, indent=2)

        print(f"Saved grouped results → {output_file}")

    # Optional Spark postprocessing example
    spark = get_spark_session("HHSim Analysis")
    for source_file in experiments:
        base_name = os.path.splitext(source_file)[0]
        result_file = os.path.join(output_dir, f"{base_name}_results.json")
        df = load_flat_sim_params(spark, result_file)

        print(f"\n[Summary stats for {base_name}]")
        summary = SparkAnalysis.compute_summary_stats(df)
        summary.show()

        print(f"\n[High g_Na sims from {base_name}]")
        high_gNa = filter_by_param(df, "g_Na", 150)
        high_gNa.show()
