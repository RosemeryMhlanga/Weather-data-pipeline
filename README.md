# Weather Data Engineering Pipeline

## Project Overview

This project implements an end-to-end weather data engineering pipeline using Python, the Open-Meteo API, pandas, SQL, SQLite, and Apache Airflow.

The pipeline extracts seven days of weather forecast data for Pretoria, Johannesburg, and Cape Town, performs data transformation and quality validation, and loads the results into a SQLite data warehouse designed using a star schema.

The project supports two data integration architectures:

**ETL (Extract, Transform, Load)**

`Extract → Transform → Validate → Load`

**ELT (Extract, Load, Transform)**

`Extract → Load to Staging → Transform → Validate → Load to Final Tables`

Both workflows have been executed successfully. The ETL workflow is also orchestrated using Apache Airflow, with a daily schedule and task-level monitoring.

The project demonstrates modular programming, REST API integration, data quality validation, dimensional modelling, SQL database operations, workflow orchestration, logging, and exception handling.

## Technologies Used

- Python
- pandas
- requests
- SQLite and SQL
- Apache Airflow 3.3.2
- Pendulum
- Ubuntu 26.04.1 LTS through WSL2
- pytest
- Git and GitHub
- Visual Studio Code

## Data Source

Weather data is retrieved from the Open-Meteo Weather API, which provides forecast data without requiring an API key.

The extracted attributes include weather codes, maximum and minimum temperatures, average temperature, precipitation, maximum wind speed, forecast dates, and geographic coordinates.

### Locations

The pipeline processes weather forecasts for Pretoria, Johannesburg, and Cape Town, South Africa.

## Project Structure

```text
Weather-data-pipeline/
│
├── dags/
│   └── weather_etl_dag.py
│
├── data/
│   ├── raw/
│   │   └── weather_raw.json
│   ├── processed/
│   │   └── weather_transformed.csv
│   └── weather.db
│
├── sql/
│   └── schema.sql
│
├── src/
│   ├── __init__.py
│   ├── extract.py
│   ├── transform.py
│   ├── validate.py
│   ├── load.py
│   ├── etl.py
│   ├── elt.py
│   ├── pipeline.py
│   ├── python_run_workflows.py
│   └── check_database.py
│
├── tests/
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

The structure shows the main project components used during development. Airflow's installed DAG file and its Ubuntu configuration are maintained separately within the local WSL2 environment.

## ETL Pipeline

### 1. Extract

The extraction stage requests forecast data from Open-Meteo for the three configured cities.

The process checks API responses, handles connection failures, records extraction events and saves the raw JSON responses.

Source module: `src/extract.py`

Raw output: `data/raw/weather_raw.json`

### 2. Transform

The transformation stage converts nested API responses into structured pandas DataFrames containing one record per location and forecast date.

The process includes:

- Flattening nested JSON records
- Standardising location names
- Converting dates and numeric measurements
- Calculating average temperature
- Removing duplicate location/date combinations
- Handling missing critical values
- Sorting records by location and observation date

Average temperature is calculated as:

`(temperature_max + temperature_min) / 2`

Source module: `src/transform.py`

### 3. Validate

Before loading, the pipeline performs data quality checks, including required-column validation, null checks, duplicate detection, temperature-range validation, nonnegative precipitation and wind-speed checks, and date-type validation.

Invalid datasets raise errors that prevent the normal loading sequence from proceeding.

Source module: `src/validate.py`

### 4. Load

Validated records are loaded into the SQLite data warehouse.

The loading process creates the required tables and populates the location dimension, date dimension and weather fact table.

Source module: `src/load.py`

Database: `data/weather.db`

## ELT Workflow

The project also implements an ELT workflow.

Unlike ETL, which transforms data before loading, the ELT workflow first loads raw extracted data into a staging table.

The sequence is:

1. Extract weather data from Open-Meteo.
2. Load raw data into `staging_weather_raw`.
3. Read staged weather records.
4. Transform the staged responses into a structured DataFrame.
5. Validate the transformed data.
6. Load the results into the final dimensional tables.

Source module: `src/elt.py`

Both ETL and ELT workflows were successfully executed from the Python project.

## Data Warehouse Design

The SQLite database uses a star-schema architecture with two dimension tables and one fact table.

### `dim_location`

Stores unique location attributes, including location identifiers, location names, latitude and longitude.

### `dim_date`

Stores calendar attributes associated with forecast observation dates, including date identifiers, day, month, year and day of the week.

### `fact_weather`

Stores measurable weather observations and foreign keys referencing the location and date dimensions.

The fact table includes maximum temperature, minimum temperature, average temperature, precipitation, wind speed and weather code measurements.

### Staging Table

`staging_weather_raw` stores raw weather data used by the ELT workflow.

The database also contains SQLite's internal `sqlite_sequence` table.

The database is inspected using `src/check_database.py`.

## Apache Airflow Orchestration

### Overview

Apache Airflow was successfully installed and configured on Ubuntu through Windows Subsystem for Linux 2 (WSL2).

Airflow orchestrates the ETL pipeline as a Directed Acyclic Graph (DAG), managing execution order, scheduling, task monitoring and retries.

**DAG ID:** `weather_etl_pipeline`

**DAG file:** `dags/weather_etl_dag.py`

**Airflow version:** 3.3.2

**Scheduling frequency:** Daily

**Configured timezone:** Africa/Johannesburg

### DAG Tasks

The workflow consists of four dependent tasks:

```text
extract_weather
      |
      v
transform_weather
      |
      v
validate_weather
      |
      v
load_weather
```

The extraction task retrieves the weather API responses. The transformation task prepares the data, the validation task checks its quality, and the loading task writes validated records to SQLite.

### Scheduling Configuration

The DAG uses daily scheduling:

```python
schedule="@daily"
```

It is configured with:

```python
catchup=False
max_active_runs=1

default_args={
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}
```

The DAG also uses the `Africa/Johannesburg` timezone.

These settings provide daily scheduling, prevent overlapping DAG runs and allow failed tasks to retry after temporary errors.

### Successful Airflow Execution

On 22 October 2026, the weather ETL DAG was successfully executed through Apache Airflow.

The Airflow dashboard confirmed:

| Metric | Result |
|---|---|
| DAG | `weather_etl_pipeline` |
| Execution status | Success |
| Successful tasks | 4 of 4 |
| Failed tasks | 0 |
| Failed DAG runs | 0 |
| Observed run duration | Approximately 19 seconds |

The four tasks — `extract_weather`, `transform_weather`, `validate_weather` and `load_weather` — completed successfully during the observed execution.

This confirms successful local workflow orchestration. Continuous unattended scheduling and database idempotency remain separate reliability considerations.

## Apache Airflow Installation and Setup

Airflow runs inside Ubuntu through WSL2 rather than directly inside native Windows PowerShell.

### 1. Open Ubuntu

Open the Ubuntu terminal from the Windows Start menu.

### 2. Navigate to the Airflow directory

```bash
cd ~/airflow-project
```

### 3. Activate the virtual environment

```bash
source airflow_venv/bin/activate
```

### 4. Configure Airflow Home

```bash
export AIRFLOW_HOME=~/airflow-project/airflow
```

### 5. Start Apache Airflow

```bash
airflow standalone
```

For convenience, these commands can be grouped into a custom shell function named `start-airflow`.

### 6. Open the Airflow dashboard

Open the following address in a browser:

http://localhost:8080

Sign in using the locally configured Airflow credentials.

### 7. Run the DAG

In the Airflow interface:

1. Select **Dags**.
2. Open `weather_etl_pipeline`.
3. Click **Trigger** to start a manual DAG run.
4. Inspect the **Runs** tab for execution progress.
5. Review individual task logs to diagnose failures.

When the DAG is unpaused and the scheduler is running, Airflow can create scheduled daily runs automatically.

**Local scheduling limitation:** The scheduler must remain running. Shutting down the laptop or stopping Ubuntu/Airflow interrupts automatic execution.

## Running ETL and ELT Manually

The pipelines can also be executed without Airflow using the project's Python virtual environment.

From the project root on Windows:

```powershell
.\.venv\Scripts\python.exe -m src.python_run_workflows
```

This runs the ETL workflow followed by the ELT workflow.

The workflows depend on the Open-Meteo API, installed Python dependencies and correctly configured database paths.

## Database Validation

A Python validation script is used to inspect the SQLite database and retrieve table names and record counts.

During validation, the database contained:

| Table | Observed row count |
|---|---:|
| `dim_location` | 3 |
| `dim_date` | 14 |
| `fact_weather` | 42 |
| `staging_weather_raw` | 3 |

These are observed counts from the local database at the time of inspection, not fixed expected values.

The ETL workflow previously processed 21 transformed records in one execution. Additional records may reflect separate ETL/ELT loads, different forecast periods or repeated execution.

Further source-to-target reconciliation and duplicate-key validation are required to establish whether every stored record is unique and accurate.

## Logging and Monitoring

The project uses Python logging and Airflow task logs.

Monitored activities include API extraction, transformation, validation, database creation, dimension loading, fact loading, task failures and workflow completion.

The Airflow interface provides visibility into DAG runs, task status, execution duration and task-level logs.

## Testing

The project includes a `tests` directory intended for pytest-based unit testing.

The test scope includes transformation logic, required fields, derived measurements, missing values, duplicate records and invalid weather values.

Tests can be executed using:

```bash
pytest
```

A complete passing test-suite result has not yet been verified.

## Known Limitations

- Apache Airflow is currently hosted locally through Ubuntu WSL2 and is not continuously available when the machine is switched off.
- The daily schedule is configured, but sustained unattended execution has not yet been verified.
- Database idempotency and duplicate prevention require further testing.
- Source-to-target reconciliation remains to be completed.
- Complete unit-test coverage and successful test results have not yet been established.
- Production deployment, external monitoring and automated failure notifications have not yet been implemented.

## Future Improvements

- Implement and verify idempotent database loading using appropriate unique constraints and upsert logic.
- Complete source-to-target reconciliation across ETL, ELT and database tables.
- Expand automated unit and integration tests.
- Add structured error alerts and pipeline health notifications.
- Introduce incremental loading where appropriate.
- Add more South African cities and historical weather data.
- Implement a persistent production-grade database.
- Deploy Airflow and the weather pipeline to an always-running cloud or server environment.
- Improve execution monitoring, observability and operational documentation.

## Project Status

**Core ETL pipeline:** Completed and successfully executed.

**ELT workflow:** Completed and successfully executed locally.

**SQLite star-schema implementation:** Completed.

**Apache Airflow orchestration:** Successfully implemented and tested through a four-task DAG run.

**Daily scheduling configuration:** Implemented.

**Production reliability:** Further validation and deployment work required.

## Author

Rosemery Mhlanga

Developed as part of the AICA Data Engineering Capstone Project.
