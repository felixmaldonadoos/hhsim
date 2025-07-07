## this file simply runs the model for a predefined number of steps

import os
from config.confighandler import ConfigHandler
from model import Model
from modelparams import ModelParams

def run_simulation(params, sim_id):
    print(f"Running simulation: {sim_id}")

    # Pass params as dictionary to Model
    model = Model(params.to_dict())

    duration = params.duration
    dt = params.dt
    I_ext = params.I_ext
    num_steps = int(duration / dt)

    results = {
        "time": [],
        "V": []
    }

    time = 0.0
    for _ in range(num_steps):
        model.step(dt, I_ext)
        results["time"].append(time)
        results["V"].append(model.V)
        time += dt

    return results

if __name__ == "__main__":
    # Load config(s)
    config_path = "config/tests"  # Adjust if needed
    handler = ConfigHandler()
    handler.load_all_configs(config_path)

    # Output directory
    output_dir = "outputs/traces"
    os.makedirs(output_dir, exist_ok=True)

    # Run each simulation
    for sim_id, config in handler.configs.items():
        params = ModelParams(config)  # fills defaults
        data = run_simulation(params, sim_id)

        output_file = os.path.join(output_dir, f"{sim_id}.csv")
        with open(output_file, 'w') as f:
            f.write("time,V\n")
            for t, v in zip(data["time"], data["V"]):
                f.write(f"{t},{v}\n")

        # print(f"Finished simulation: {sim_id} → saved to {output_file}")
