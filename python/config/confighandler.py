import os
import json

# Simple configuration handler that reads .json config files

class ConfigHandler:
    def __init__(self):
        self.configs = {}

    def _load_config(self, file_path):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Configuration file {file_path} does not exist.")
        
        with open(file_path, 'r') as f:
            config_data = json.load(f)
        
        sim_id = config_data.get("sim_id")
        if not sim_id:
            raise ValueError(f"Missing 'sim_id' in config: {file_path}")
        
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
    print(handler.configs)
