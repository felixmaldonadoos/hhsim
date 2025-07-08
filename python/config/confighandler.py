import os
import json

# Configuration handler that reads .json config files, each with one or more simulations

class ConfigHandler:
    def __init__(self):
        self.configs = {}  # Maps sim_id → config dict

    def _load_config(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Configuration file {file_path} does not exist.")
        
        with open(file_path, 'r') as f:
            all_configs = json.load(f)

        if not isinstance(all_configs, dict):
            raise ValueError(f"Top-level JSON structure must be a dictionary: {file_path}")

        for sim_id, config_data in all_configs.items():
            if not isinstance(config_data, dict):
                print(f"Skipping entry {sim_id}: not a valid dict")
                continue

            # Inject sim_id if missing
            if "sim_id" not in config_data:
                config_data["sim_id"] = sim_id

            # Add source file name to each config
            config_data["_source_file"] = os.path.basename(file_path)

            self.configs[sim_id] = config_data

    def load_all_configs(self, directory_path):
        if not os.path.isdir(directory_path):
            raise NotADirectoryError(f"{directory_path} is not a valid directory.")
        
        for filename in os.listdir(directory_path):
            if filename.endswith(".json"):
                full_path = os.path.join(directory_path, filename)
                try:
                    self._load_config(full_path)
                except Exception as e:
                    print(f"Skipping {filename}: {e}")

if __name__ == "__main__":
    handler = ConfigHandler()
    handler.load_all_configs("tests/")

    if handler.configs:
        # Get the last added (sim_id, config) pair
        last_sim_id = list(handler.configs.keys())[-1]
        last_config = handler.configs[last_sim_id]

        print(f"Last sim ID: {last_sim_id}")
        print(json.dumps(last_config, indent=2))
    else:
        print("No valid configs loaded.")
