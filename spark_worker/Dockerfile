FROM spark:4.0.0-scala2.13-java21-ubuntu

USER root

RUN set -ex; \
    apt-get update; \
    apt-get install -y python3 python3-pip git; \
    rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir pyspark numpy tqdm

COPY postgresql-42.7.7.jar /opt/spark/jars/
USER spark


CMD ["bash"]

# call spark worker with: 
# $SPARK_HOME/sbin/start-worker.sh spark://<SPARK_MASTER_IP>:<SPARK_MASTER_PORT>
