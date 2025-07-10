import os, sys
import psycopg2
# import postgresql_config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from helpers import logger
from . import connection
from . import postgresql_config

import json
import os
import psycopg2

from pathlib import Path

def load_configs(folder):
    configs = []
    for path in Path(folder).glob("*.json"):
        with open(path) as f:
            data = json.load(f)
        config = data.copy()
        config["config_name"] = path.stem  # e.g., "exp01" from "exp01.json"
        configs.append(config)
    return configs

def upload_configs(rows, conn):
    with conn.cursor() as cur:
        for row in rows:
            keys = row.keys()
            values = list(row.values())
            columns = ', '.join(keys)
            placeholders = ', '.join(['%s'] * len(values))
            update_clause = ', '.join([f"{key} = EXCLUDED.{key}" for key in keys if key != 'sim_id'])

            sql = f"""
                INSERT INTO simulation_configs ({columns})
                VALUES ({placeholders})
                ON CONFLICT (sim_id) DO UPDATE SET {update_clause}
            """
            cur.execute(sql, values)
            conn.commit()
        print(f"Inserted {len(rows)} rows.")
    
def get_configs_from_db(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM simulation_configs")
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in rows]
