#!/bin/bash

echo "Setting up environment variables for Spark and PostgreSQL..."
export SPARK_HOME="$HOME/.local/bin/spark-4.0.0"
export SPARK_MASTER_IP=<your_ip>
export SPARK_MASTER_PORT=<your_port>
export SPARK_MASTER_WEBUI_PORT=<your_ui_port>

export PATH="$PATH:$SPARK_HOME/bin"
export SPARK_POSTGRESQL_IP=<your_ip>
export SPARK_POSTGRESQL_PORT=<your_port>
export SPARK_POSTRESQL_USER=<your_username>
export SPARK_POSTGRESQL_PW=<your_password>

echo "Environment variables set up successfully."

echo "Installiing python dependencies..."
pip install --upgrade pip
pip install pyqt5 pyqtdarktheme matplotlib numpy pyspark tqdm psycopg2

echo "Python dependencies installed successfully."

sudo apt-get install libpq-dev build-essential