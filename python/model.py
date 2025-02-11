# model.py
import numpy as np

class Model:
    def __init__(self):
        
        self.neuron_params = {
            "C_m": ("Membrane Capacitance (µF/cm²):", 0.1, 5.0, 1.0),
            "g_Na": ("Sodium Conductance (mS/cm²):", 50.0, 200.0, 120.0),
            "g_K": ("Potassium Conductance (mS/cm²):", 10.0, 100.0, 36.0),
            "g_L": ("Leak Conductance (mS/cm²):", 0.1, 2.0, 0.3),
            "E_Na": ("Sodium Reversal Potential (mV):", 40.0, 70.0, 50.0),
            "E_K": ("Potassium Reversal Potential (mV):", -100.0, -50.0, -77.0),
            "E_L": ("Leak Reversal Potential (mV):", -70.0, -30.0, -54.387)
        }
        
        # Hodgkin–Huxley parameters (classic values)
        self.C_m  = self.neuron_params['C_m'][3]
        self.g_Na = self.neuron_params['g_Na'][3]
        self.g_K  = self.neuron_params['g_K'][3]
        self.g_L  = self.neuron_params['g_L'][3]
        self.E_Na = self.neuron_params['E_Na'][3]
        self.E_K  = self.neuron_params['E_K'][3]
        self.E_L  = self.neuron_params['E_L'][3]

        # Initial conditions (resting state ~ -65 mV)
        self.V = -65.0
        self.m = self.alpha_m(self.V) / (self.alpha_m(self.V) + self.beta_m(self.V))
        self.h = self.alpha_h(self.V) / (self.alpha_h(self.V) + self.beta_h(self.V))
        self.n = self.alpha_n(self.V) / (self.alpha_n(self.V) + self.beta_n(self.V))

    def safe_exp(self, x):
        """Clips x to the range [-50, 50] before applying exp to avoid overflow."""
        return np.exp(np.clip(x, -50, 50))

    def alpha_n(self, V):
        if abs(V + 55) < 1e-6:
            return 0.1
        return 0.01 * (V + 55) / (1 - self.safe_exp(-(V + 55) / 10))

    def beta_n(self, V):
        return 0.125 * self.safe_exp(-(V + 65) / 80)

    def alpha_m(self, V):
        if abs(V + 40) < 1e-6:
            return 1.0
        return 0.1 * (V + 40) / (1 - self.safe_exp(-(V + 40) / 10))

    def beta_m(self, V):
        return 4.0 * self.safe_exp(-(V + 65) / 18)

    def alpha_h(self, V):
        return 0.07 * self.safe_exp(-(V + 65) / 20)

    def beta_h(self, V):
        return 1 / (1 + self.safe_exp(-(V + 35) / 10))

    def step(self, dt, I_ext):
        """Advances the model by one time step using Euler's method."""
        dm = self.alpha_m(self.V) * (1 - self.m) - self.beta_m(self.V) * self.m
        dh = self.alpha_h(self.V) * (1 - self.h) - self.beta_h(self.V) * self.h
        dn = self.alpha_n(self.V) * (1 - self.n) - self.beta_n(self.V) * self.n

        self.m += dt * dm
        self.h += dt * dh
        self.n += dt * dn

        I_Na = self.g_Na * (self.m ** 3) * self.h * (self.V - self.E_Na)
        I_K  = self.g_K * (self.n ** 4) * (self.V - self.E_K)
        I_L  = self.g_L * (self.V - self.E_L)

        dV = (I_ext - I_Na - I_K - I_L) / self.C_m
        self.V += dt * dV
