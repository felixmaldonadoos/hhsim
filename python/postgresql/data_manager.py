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

def generate_params_table(conn):
    with conn.cursor() as cur:
        # Check if the table already exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'simulation_configs'
            );
        """)
        table_exists = cur.fetchone()[0]
        
        if table_exists:
            print("Table 'simulation_configs' already exists.")
            return
        print('Creating table "simulation_configs"...')
        cur.execute("""
            CREATE TABLE IF NOT EXISTS simulation_configs (
                id SERIAL PRIMARY KEY,
                sim_id TEXT UNIQUE,
                C_m FLOAT,
                g_Na FLOAT,
                g_K FLOAT,
                g_L FLOAT,
                E_Na FLOAT,
                E_K FLOAT,
                E_L FLOAT,
                I_ext FLOAT,
                duration FLOAT,
                dt FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("'simulation_configs' created")

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

def generate_results_table(conn):
    with conn.cursor() as cur:
        # Check if the table already exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_name = 'simulation_results'
            );
        """)
        table_exists = cur.fetchone()[0]
        
        if table_exists:
            print("Table 'simulation_results' already exists.")
            return
        print('Creating table "simulation_configs"...')
        cur.execute("""
            CREATE TABLE IF NOT EXISTS simulation_results (
                id SERIAL PRIMARY KEY,
                sim_id TEXT REFERENCES simulation_configs(sim_id) ON DELETE CASCADE,
                time_series FLOAT[],
                voltage_series FLOAT[],
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        print("'simulation_results' created")
        
def upload_simulation_result_row(conn, sim_data:dict=None):
    with conn.cursor() as cur:
        sql = """
            INSERT INTO simulation_results (sim_id, time_series, voltage_series)
            VALUES (%s, %s, %s)
            RETURNING id;
        """
        cur.execute(sql, (sim_data.sim_id, sim_data.time, sim_data.V))
        new_id = cur.fetchone()[0]
        conn.commit()
        print(f"Inserted simulation result for '{sim_data.sim_id}' with result ID: {new_id}")
