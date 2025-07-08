# spark/transformer.py
from pyspark.sql import DataFrame
from pyspark.sql.functions import col

def filter_by_param(df: DataFrame, param_name: str, threshold: float) -> DataFrame:
    return df.filter(col(param_name) > threshold)


def select_columns(df: DataFrame, columns: list) -> DataFrame:
    return df.select(["sim_id"] + columns)