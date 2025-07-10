import psycopg2
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from . import postgresql_config

from helpers import logger
# from helpers import logger

class PostgresConnectionManager:
    def __init__(self, config: postgresql_config.PostgresConfig):
        self.logger = logger.Logger("PostgresConnectionManager")
        self.logger.log("Initializing PostgresConnectionManager")
        # log.info("Initializing PostgresConnectionManager")
        self.config = config
        self.connection = None

    def connect(self):
        if self.connection is not None:
            return  # Already connected

        try:
            self.connection = psycopg2.connect(
                host=self.config.host_ip,
                dbname=self.config.dbname,
                user=self.config.user,
                password=self.config.password,
                port=self.config.port
            )
            self.logger.log("Connection established successfully.",bSuccess=True)
        except Exception as e:
            self.logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
            
        if self.connection: 
            return self.connection, self.connection.cursor()
        raise Exception("Connection not established. Call connect() first.")

    def get_cursor(self):
        if self.connection is None:
            raise Exception("Connection not established. Call connect() first.")
        return self.connection.cursor()
        
    def close(self):
        if self.connection is not None:
            self.connection.cursor().close()
            self.connection.close()
            self.connection = None
            self.logger.log("Connection closed.",bSuccess=True)
        else:
            self.logger.warn("Connection is already closed or was never established.")
            # log.warn("Connection is already closed or was never established.")