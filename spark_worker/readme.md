
# Docker & Apache Spark


## Installation 

For now, this will only include installation of spar in docker. In this repo, I supplies a `Dockerfile` pre-configured to use `pyspark`.

### Build Docker 

A bash script has been provided to build the docker image and to run it - `builddocker.sh`. If you decide to modify it or add your own, make sure to make the file an executable: 

```bash
chmod +x builddocker.sh
```

Apply the same for `rundocker.sh`.

To run the executable, simply do: 
Run: 

```bash
./builddocker.sh
```

Alternatively, to run the image: 

```bash
./rundocker.sh
```

### Docker

## Master-Worker Basic Setup and Test

This subsection shows how to connect a worker node to the master node.

### Master

#### Start 

```bash
SPARK_LOCAL_IP=<host_ip> $SPARK_HOME/sbin/start-master.sh --host <host_ip>
```

#### Stop

```bash
$SPARK_HOME/sbin/stop-master.sh
```

### Worker

#### Start

```bash
$SPARK_HOME/sbin/start-worker.sh spark://<host_ip>:7077
```

#### Stop

```bash
$SPARK_HOME/sbin/stop-worker.sh
```