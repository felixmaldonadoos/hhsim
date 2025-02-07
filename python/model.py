# model.py
import numpy as np

class Model:
    def __init__(self):
        # Hodgkin–Huxley parameters (classic values)
        self.C_m  = 1.0      # membrane capacitance (µF/cm²)
        self.g_Na = 120.0    # sodium conductance (mS/cm²)
        self.g_K  = 36.0     # potassium conductance (mS/cm²)
        self.g_L  = 0.3      # leak conductance (mS/cm²)
        self.E_Na = 50.0     # sodium reversal potential (mV)
        self.E_K  = -77.0    # potassium reversal potential (mV)
        self.E_L  = -54.387  # leak reversal potential (mV)

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
