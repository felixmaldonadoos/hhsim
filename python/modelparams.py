class ModelParams:
    def __init__(self, config_dict=None):
        # Full parameter metadata with defaults as the last item in each tuple
        self.neuron_params = {
            "C_m":  ("Membrane Capacitance (µF/cm²):", 0.1, 5.0, 1.0),
            "g_Na": ("Sodium Conductance (mS/cm²):", 50.0, 200.0, 120.0),
            "g_K":  ("Potassium Conductance (mS/cm²):", 10.0, 100.0, 36.0),
            "g_L":  ("Leak Conductance (mS/cm²):", 0.1, 2.0, 0.3),
            "E_Na": ("Sodium Reversal Potential (mV):", 40.0, 70.0, 50.0),
            "E_K":  ("Potassium Reversal Potential (mV):", -100.0, -50.0, -77.0),
            "E_L":  ("Leak Reversal Potential (mV):", -70.0, -30.0, -54.387)
        }

        # Config dict from JSON (can be None)
        config_dict = config_dict or {}
        
        # Assign values from config, fallback to default
        for key, (_, _, _, default) in self.neuron_params.items():
            setattr(self, key, config_dict.get(key, default))

        # Additional non-biophysical params (duration, dt, I_ext)
        self.I_ext = config_dict.get("I_ext", 0.0)
        self.duration = config_dict.get("duration", 50.0)
        self.dt = config_dict.get("dt", 0.01)

    def to_dict(self):
        return {
            key: getattr(self, key)
            for key in self.neuron_params.keys()
        } | {
            "I_ext": self.I_ext,
            "duration": self.duration,
            "dt": self.dt
        }
