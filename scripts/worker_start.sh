#!/bin/bash
echo "Starting worker..."
$SPARK_HOME/sbin/start-worker.sh spark://$SPARK_MASTER_IP:7077