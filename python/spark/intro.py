from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode
import os

# Step 1: Create SparkSession
spark = SparkSession.builder \
    .appName("ExtractParams") \
    .master("local[*]") \
    .getOrCreate()

# Step 2: Load JSON (with multiline)
file_path = os.path.join("test", "test02_config_results.json")
df = spark.read.option("multiline", "true").json(file_path)

# Step 3: Extract the `sims` map dynamically using .select("sims.*")
sims_struct = df.select("sims.*")  # gives columns like exp01, exp02, etc.

# Step 4: Convert to map type dynamically
# - Turn struct columns into a map (key: sim_id, value: struct)
sim_map = sims_struct.selectExpr(
    "map(" + ", ".join(
        [f"'{field.name}', `{field.name}`" for field in sims_struct.schema.fields]
    ) + ") as sims_map"
)

# Step 5: Explode the map
exploded = sim_map.select(
    explode("sims_map").alias("sim_id", "sim_struct")
)

# Step 6: Extract params
sim_params = exploded.select(
    col("sim_id"),
    col("sim_struct.data.params").alias("params")
)

# Step 7: Flatten
sim_params_flat = sim_params.select(
    "sim_id",
    "params.*"
)

# Step 8: Display
sim_params_flat.show(truncate=False)
