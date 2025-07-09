#!/bin/bash
echo "Starting Spark master..."
SPARK_LOCAL_IP=$SPARK_MASTER_IP $SPARK_HOME/sbin/start-master.sh --host $SPARK_MASTER_IP