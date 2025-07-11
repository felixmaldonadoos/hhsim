#!/bin/bash

IMAGE_NAME="spark_worker"

CONTAINER_NAME="spark_worker_0"

SPARK_MASTER_URL="spark://$SPARK_MASTER_IP:$SPARK_MASTER_PORT"

echo "Running ccontainer: $CONTAINER_NAME"

docker run -it --rm \
	--name $CONTAINER_NAME \
	$IMAGE_NAME \
	bash
