# hhsim

**hhsim** is a Python-based simulation of the Hodgkin-Huxley neuron model, featuring a simple graphical interface built with PyQt5. It allows users to explore the dynamics of action potential generation by adjusting key biophysical parameters in real time.

This project uses `Apache Spark` to distribute processing load  and `PostreSQL` database for up/downloading data.  [WIP]

## Setup

### Spark IP


Set spark `$SPARK_MASTER_IP`. This will be handled by `setup.sh` but that is still a WIP.  

```bash
export SPARK_MASTER_IP=<your_ip>
```

## Features

- Interactive GUI for adjusting:
  - Membrane capacitance
  - Sodium, potassium, and leak conductances
  - Reversal potentials
- Real-time simulation of action potentials using the classical Hodgkin-Huxley equations
- Visualization of membrane voltage over time
- Modular and extensible codebase

## Requirements

- Python 3.8+
- PyQt5
- NumPy
- Matplotlib (optional, if plotting is included)

Install dependencies with:

```bash
pip install pyqt5 pyqtdarktheme matplotlib numpy pyspark tqdm
```