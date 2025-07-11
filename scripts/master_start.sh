#!/bin/bash
echo "Starting Spark master..."
SPARK_LOCAL_IP=$SPARK_MASTER_IP $SPARK_HOME/sbin/start-master.sh \
    --host $SPARK_MASTER_IP \
    --port $SPARK_MASTER_PORT \
    --webui-port $SPARK_MASTER_WEBUI_PORT

log_file=$(ls -t "$SPARK_HOME/logs/spark-"*"-org.apache.spark.deploy.master.Master-"*"-alex.out" | head -n 1)

master_url=$(grep -Eo 'spark://[0-9.]+:[0-9]+' "$log_file")
webui_url=$(grep -Eo 'http://[0-9.]+:[0-9]+' "$log_file")

echo "Master: $master_url"
echo "webUI: $webui_url"
