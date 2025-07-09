#!/bin/bash

IMAGE_NAME="spark_worker"

CONTAINER_NAME="spark_worker_0"

SPARK_MASTER_URL="spark://192.168.1.100:7077"

echo "Running ccontainer: $CONTAINER_NAME"

docker run -it --rm \
	--name $CONTAINER_NAME \
	$IMAGE_NAME \
	bash
