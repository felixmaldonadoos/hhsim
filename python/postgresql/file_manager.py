import os
import psycopg2
import postgresql_config
import connection
from helpers import logger

config = postgresql_config.PostgresConfig()
loggy = logger.Logger("PostgresConfig")
loggy.log("PostgresConfig initialized")

connmanager = connection.PostgresConnectionManager(config)
conn, cursor = connmanager.connect()

conn.commit()
connmanager.close()


