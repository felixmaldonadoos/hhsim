# Parallel Simulation and Spark Analysis Framework for HHSim

This document outlines a step-by-step plan for extending the `hhsim` project with large-scale simulation capabilities and batch data analysis using Apache Spark.

## 1. Parallel Simulation + Spark Analysis Framework

### 1.1 Implement Config-Based Simulation Runner

#### 1.1.1 Config Reader Class

* Create a Python class that reads simulation parameters from `.json` configuration files.
* Each config file should define parameters such as:

  * Sodium and potassium conductances (e.g., `gNa`, `gK`)
  * External current (`I_ext`)
  * Time step and simulation duration
* The class should:

  * Parse the config
  * Validate input values and apply defaults where necessary
  * Execute a simulation using the `hhsim` engine

#### 1.1.2 Support Batch Execution

* Extend the runner to accept a directory of `.json` config files
* Automatically iterate over each config
* For each simulation:

  * Run the model
  * Store outputs using a unique identifier (e.g., `sim_0001`)

---

### 1.2 Save Simulation Outputs for Spark Ingestion

#### 1.2.1 Define Output Format

* Store simulation results in a structured, efficient format:

  * Time series: membrane voltage over time
  * Metadata: parameters used for that simulation
* Recommended formats:

  * CSV or JSON for each simulation
  * Optionally Parquet for Spark performance

#### 1.2.2 Output Directory Structure

* Organize results into folders:

  ```
  outputs/
    ├── metadata/
    │     ├── sim_0001.json
    │     ├── sim_0002.json
    │     └── ...
    └── traces/
          ├── sim_0001.csv
          ├── sim_0002.csv
          └── ...
  ```

#### 1.2.3 (Optional) Generate Master Index

* Combine metadata into a single `index.csv` for quick lookup and joins
* Include: `sim_id`, parameters, basic stats (e.g., spike count, duration)

---

### 1.3 Batch Analysis with Apache Spark

#### 1.3.1 Load Simulation Data into Spark

* Read all trace files into a Spark DataFrame
* Join with corresponding config metadata (if separated)

#### 1.3.2 Define Analysis Pipeline

* For each simulation:

  * Count spikes (voltage threshold crossings)
  * Compute firing rate: `spike_count / duration`
  * Calculate mean and variance of interspike intervals (ISIs)
  * Determine min, max, and resting membrane potential

#### 1.3.3 Save Processed Results

* Store output summary for each simulation:

  * Format: Parquet or CSV
  * Example structure:

    ```
    sim_id | gNa | gK | I_ext | spike_count | firing_rate | mean_ISI | min_V | max_V
    ```

---

### 1.4 Query with Spark SQL

#### 1.4.1 Example SQL Queries

* Filter high-firing simulations:

  ```sql
  SELECT * FROM sim_summary WHERE spike_count > 20;
  ```

* Correlate input current with firing rate:

  ```sql
  SELECT CORR(firing_rate, I_ext) FROM sim_summary;
  ```

* Identify bursting behavior:

  ```sql
  SELECT * FROM sim_summary
  WHERE spike_count > 10 AND mean_ISI < 5;
  ```

#### 1.4.2 Export or Visualize

* Export filtered results to CSV for plotting
* Optionally, build visualizations in Python or use a dashboard (e.g., Jupyter, Streamlit)

---

## Next Step

Once the parallel simulation and batch analysis are functional, the next extension will focus on model tuning and automatic discovery of neuron behaviors using ML pipelines.
