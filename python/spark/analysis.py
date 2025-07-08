# spark/analysis.py
from pyspark.sql import DataFrame
from pyspark.sql.functions import avg, col

class SparkAnalysis:
    
    @staticmethod
    def compute_summary_stats(df: DataFrame, group_by_field: str = None) -> DataFrame:
        numeric_cols = [c for c in df.columns if c != "sim_id"]
        agg_exprs = [avg(col(c)).alias(f"avg_{c}") for c in numeric_cols]
        return df.groupBy().agg(*agg_exprs)