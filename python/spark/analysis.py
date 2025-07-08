from pyspark.sql import DataFrame, SparkSession, Row
from pyspark.sql.functions import avg, col
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
import numpy as np
from helpers.logger import Logger
from helpers.progessbar import ProgressBar
class SparkAnalysis:
    
    @staticmethod
    def compute_summary_stats(df: DataFrame, group_by_field: str = None) -> DataFrame:
        numeric_cols = [c for c in df.columns if c != "sim_id"]
        agg_exprs = [avg(col(c)).alias(f"avg_{c}") for c in numeric_cols]
        return df.groupBy().agg(*agg_exprs)
    
    @staticmethod
    def detect_spikes(df: DataFrame = None, 
                      voltage_col: str = "V", 
                      threshold: float = -40.0, 
                      resting: float = -70.0, 
                      epsilon: float = 1.0) -> dict[str, list[tuple[int, int]]]:
        import time
        logger = Logger("SparkAnalysis")
        spikes_by_sim = {}

        pb = ProgressBar(total=df.count(), prefix="Detecting spikes")
        for i, row in enumerate(df.collect()):
            sim_id = row["sim_id"]
            voltage_series = np.asarray(row[voltage_col], dtype=np.float64)

            # logger.log(f"Detecting spikes for {sim_id}...", sim_id)

            # mask of where voltage exceeds threshold
            above_thresh = voltage_series > threshold
            if not np.any(above_thresh):
                spikes_by_sim[sim_id] = []
                continue

            # detect rising and falling edges
            diff = np.diff(above_thresh.astype(int))
            starts = np.where(diff == 1)[0] + 1
            ends = np.where(diff == -1)[0] + 1

            # handle edge cases
            if above_thresh[0]: starts = np.insert(starts, 0, 0)
            if above_thresh[-1]: ends = np.append(ends, len(voltage_series))

            spike_windows = list(zip(starts, ends))

            # logger.log(f"Found {len(spike_windows)} spike windows for {sim_id}", sim_id, bSuccess=True)

            spikes_by_sim[sim_id] = spike_windows
            pb.update(i, label=f"Spikes for {sim_id}")
            
        pb.finish()
        return spikes_by_sim
    
    @staticmethod
    def detect_spikes_sparkdf(spark: SparkSession,
                               df: DataFrame,
                               voltage_col: str = "V",
                               threshold: float = -40.0,
                               resting: float = -70.0,
                               epsilon: float = 1.0) -> DataFrame:
        """
        Wraps detect_spikes() and returns a Spark DataFrame with schema:
        sim_id, spike_start, spike_end
        """
        spike_dict = SparkAnalysis.detect_spikes(
            df,
            voltage_col=voltage_col,
            threshold=threshold,
            resting=resting,
            epsilon=epsilon
        )
        logger = Logger("SparkAnalysis")

        rows = []
        for sim_id, windows in spike_dict.items():
            for start, end in windows:
                rows.append(Row(sim_id=sim_id, spike_start=int(start), spike_end=int(end)))

        schema = StructType([
            StructField("sim_id", StringType(), False),
            StructField("spike_start", IntegerType(), False),
            StructField("spike_end", IntegerType(), False)
        ])

        return spark.createDataFrame(rows, schema=schema)
