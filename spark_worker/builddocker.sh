#!/bin/bash

IMAGE_NAME="spark_worker"

echo "Building Docker image: $IMAGE_NAME"

docker build -t $IMAGE_NAME .


