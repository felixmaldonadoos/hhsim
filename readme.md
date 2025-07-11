# hhsim

**hhsim** is a Python-based simulation of the Hodgkin-Huxley neuron model, featuring a simple graphical interface built with PyQt5. It allows users to explore the dynamics of action potential generation by adjusting key biophysical parameters in real time.

This project uses `Apache Spark` to distribute processing load  and `PostreSQL` database for up/downloading data.  [WIP]

## Overview and General Requirements 

### What is this thing?

- Interactive GUI for adjusting:
  - Membrane capacitance
  - Sodium, potassium, and leak conductances
  - Reversal potentials
- Real-time simulation of action potentials using the classical Hodgkin-Huxley equations
- Visualization of membrane voltage over time
- Modular and extensible codebase

### Environment Versions

| Component            | Version / Info                                   |
|----------------------|--------------------------------------------------|
| OS     | Ubuntu (WSL2 on Windows 11)                      |
| SQL Host OS         | Windows 11                                       |
| Python               | 3.10.12                                             |
| Java                 | 17.0.0.15                                    |
| Apache Spark         | 4.0.0                                            |
| PostgreSQL         | 17                                            |

You may already have these system packages installed, but always worth to double check: 

```bash
sudo apt-get install libpq-dev build-essential 
```

If you are running **without GUI**, install the following `pip` packages: 

```bash
pip install pyspark tqdm  psycopg2
```

If you are running **with GUI** (tested on `WSL2 Ubuntu 22.04`), you need to install the following `python` dependencies with:

```bash
pip install pyqt5 pyqtdarktheme matplotlib numpy pyspark tqdm psycopg2 pyarrow
```

## Setup

### Spark IP

Set spark `$SPARK_MASTER_IP`. This will be handled by `setup.sh` but that is still a WIP.  

```bash
export SPARK_HOME="$HOME/.local/bin/spark-4.0.0"
export SPARK_MASTER_IP=<your_ip>
export SPARK_MASTER_PORT=<your_port>
export SPARK_MASTER_WEBUI_PORT=<your_ui_port>
```

### PostgreSQL

You need to have a postresql server already running. To make this easier, run the following: 

```bash
export PATH=$PATH:$SPARK_HOME/bin
export SPARK_POSTGRESQL_IP=<your_ip>
export SPARK_POSTGRESQL_PORT=<your_port>
export SPARK_POSTRESQL_USER=<your_username>
export SPARK_POSTGRESQL_PW=<your_password>
```

### Spark + PostgreSQL exports

You can do set all environment variables at once by modifying `setup.sh`.

If you are running your postresql server on a windows machine and are connecting to it via `wsl`, you need to add the server's port to the list of forwarded ports. Before running main.py (or anything that attempts to connect to the postresql server) you must run the script as **administrator**: `scripts/wsl-port-forwarding.ps1`. The contents of it are: 

## Requirements

- Python 3.8+
- PyQt5
- NumPy
- Matplotlib (optional, if plotting is included)
