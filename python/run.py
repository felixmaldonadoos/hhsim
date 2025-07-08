## this file simply runs the model for a predefined number of steps

import os
import json
from config.confighandler import ConfigHandler
from model import Model
from modelparams import ModelParams
from experimentdata import SimData, ExperimentData  # new classes

def run_simulation(params, sim_id):
    print(f"Running simulation: {sim_id}")

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

    experiments = {}  # filename → ExperimentData

    for sim_id, config in handler.configs.items():
        params = ModelParams(config)
        time, voltage = run_simulation(params, sim_id)

        sim_data = SimData(sim_id, params.to_dict(), time, voltage)
        source_file = config.get("_source_file", "unknown_config.json")

        if source_file not in experiments:
            experiments[source_file] = ExperimentData(source_file)

        experiments[source_file].add_sim(sim_data)
        print(f"Finished simulation: {sim_id} (from {source_file})")

    # Save all experiment results
    for source_file, experiment in experiments.items():
        base_name = os.path.splitext(source_file)[0]
        output_file = os.path.join(output_dir, f"{base_name}_results.json")
        with open(output_file, "w") as f:
            json.dump(experiment.to_dict(), f, indent=2)

        print(f"Saved grouped results → {output_file}")
