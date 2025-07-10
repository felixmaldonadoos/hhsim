# hhsim

**hhsim** is a Python-based simulation of the Hodgkin-Huxley neuron model, featuring a simple graphical interface built with PyQt5. It allows users to explore the dynamics of action potential generation by adjusting key biophysical parameters in real time.

This project uses `Apache Spark` to distribute processing load  and `PostreSQL` database for up/downloading data.  [WIP]

## Setup

### Spark IP


Set spark `$SPARK_MASTER_IP`. This will be handled by `setup.sh` but that is still a WIP.  

```bash
export SPARK_MASTER_IP=<your_ip>
```

### PostgreSQL

You need to have a postresql server already running. To make this easier, run the following: 

```bash
export SPARK_POSTGRESQL_IP=<your_ip>
export SPARK_POSTGRESQL_PORT=<your_port>
export SPARK_POSTRESQL_USER=<your_username>
export SPARK_POSTGRESQL_PW=<your_password>
```

If you are running your postresql server on a windows machine and are connecting to it via `wsl`, you need to add the server's port to the list of forwarded ports. Before running main.py (or anything that attempts to connect to the postresql server) you must run the script as **administrator**: `scripts/wsl-port-forwarding.ps1`. The contents of it are: 

```powershell
If (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {   
  $arguments = "& '" + $myinvocation.mycommand.definition + "'"
  Start-Process powershell -Verb runAs -ArgumentList $arguments
  Break
}
$ifconfig = wsl.exe ifconfig eth0
$remoteport = $ifconfig| Select-String -Pattern "inet "
$found = $remoteport -match '\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}';

if ($found) {
  $remoteport = $matches[0];
}
else {
  Write-Output "IP address could not be found";
  exit;
}


Invoke-Expression "netsh interface portproxy reset";

$portl = $args
$portl+= "5432"
$portl+= "5433"

for ($i = 0; $i -lt $portl.length; $i++) {
  $port = $portl[$i];
  Invoke-Expression "netsh interface portproxy add v4tov4 listenport=$port connectport=$port connectaddress=$remoteport";
  Invoke-Expression "netsh advfirewall firewall add rule name=$port dir=in action=allow protocol=TCP localport=$port";
}

Invoke-Expression "netsh interface portproxy show v4tov4";
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
pip install pyqt5 pyqtdarktheme matplotlib numpy pyspark tqdm libpq-dev build-essential psycopg2
```
