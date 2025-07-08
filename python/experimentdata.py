import json

class JsonSerializableNode:
    def __init__(self, name):
        self.name = name  # e.g., "sim01" or "test01_config.json"

    def to_dict(self):
        raise NotImplementedError

    @classmethod
    def from_dict(cls, d):
        raise NotImplementedError


class SimData(JsonSerializableNode):
    def __init__(self, sim_id, params, time, V):
        super().__init__(sim_id)
        self.params = params
        self.time = time
        self.V = V

    def to_dict(self):
        return {
            "name": self.name,
            "data": {
                "params": self.params,
                "time": self.time,
                "V": self.V
            }
        }

    @staticmethod
    def from_dict(d):
        data = d["data"]
        return SimData(
            sim_id=d["name"],
            params=data["params"],
            time=data["time"],
            V=data["V"]
        )


class ExperimentData(JsonSerializableNode):
    def __init__(self, experiment_name):
        super().__init__(experiment_name)
        self.sims = {}  # sim_id → SimData

    def add_sim(self, sim_data: SimData):
        self.sims[sim_data.name] = sim_data

    def to_dict(self):
        return {
            "name": self.name,
            "sims": {
                sim_id: sim.to_dict()
                for sim_id, sim in self.sims.items()
            }
        }

    @staticmethod
    def from_dict(d):
        exp = ExperimentData(d["name"])
        for sim_id, sim_obj in d["sims"].items():
            exp.sims[sim_id] = SimData.from_dict(sim_obj)
        return exp


# === Example test/demo ===
if __name__ == "__main__":
    # Simulated data for testing
    params_dict = {
        "g_Na": 120.0,
        "g_K": 36.0,
        "g_L": 0.3,
        "E_Na": 50.0,
        "E_K": -77.0,
        "E_L": -54.387,
        "I_ext": 10.0,
        "dt": 0.01,
        "duration": 50.0
    }
    time_array = [0.0, 0.01, 0.02, 0.03]
    voltage_array = [-65.0, -64.8, -64.5, -64.2]

    # Create simulation result
    sim_data = SimData("sim01", params_dict, time_array, voltage_array)

    # Create experiment with multiple sims
    exp = ExperimentData("test01_config.json")
    exp.add_sim(sim_data)

    # Serialize to JSON
    with open("test01_results.json", "w") as f:
        json.dump(exp.to_dict(), f, indent=2)

    print("Saved test01_results.json")
