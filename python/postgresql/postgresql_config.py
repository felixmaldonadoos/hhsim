import os
class PostgresConfig:
    def __init__(self, dbname: str = "postgres"):
        self.host_ip = os.environ.get("SPARK_POSTGRESQL_IP")
        self.port = int(os.environ.get("SPARK_POSTGRESQL_PORT"))
        self.user = os.environ.get("SPARK_POSTGRESQL_USER")
        self.password = os.environ.get("SPARK_POSTGRESQL_PW")
        self.dbname = dbname
        self._validate()

    def _validate(self):
        missing = []
        for field in ['host_ip', 'port', 'user', 'password', 'dbname']:
            value = getattr(self, field)
            if value is None or (isinstance(value, str) and value.strip() == ""):
                missing.append(field)
        if missing:
            raise ValueError(f"Missing or empty PostgreSQL config fields: {', '.join(missing)}")

    def as_dict(self) -> dict:
        return {
            "host_ip": self.host_ip,
            "port": self.port,
            "user": self.user,
            "password": self.password,
            "dbname": self.dbname
        }

    def __str__(self):
        return f"PostgresConfig(host_ip={self.host_ip}, port={self.port}, user={self.user}, dbname={self.dbname})"

if __name__ == "__main__":
    import psycopg2
    config = PostgresConfig()
    print(config)             # Safe to print
    # print(config.as_dict())   # Useful for passing to psycopg2.connect(**config.as_dict())

    conn = psycopg2.connect(
        host=config.host_ip,
        dbname=config.dbname,
        user=config.user,
        password=config.password,
        port=config.port
    )

    cur = conn.cursor()

    ### START MAIN BODY ###

    cur.execute(
        """ CREATE TABLE IF NOT EXISTS person (
        id INT PRIMARY KEY,
        name VARCHAR(255),
        age INT, 
        gender CHAR
    );
                
    """)

    ### END MAIN BODY ###
    ## end 

    conn.commit()
    cur.close()
    conn.close()
    
    print('PostgreSQL table created successfully. You should now see it in pgAdmin.')