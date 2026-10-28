
import json
import logging
import sys

from datetime import timedelta
from pathlib import Path

import pandas as pd
import pendulum

from airflow.sdk import dag, task


# ============================================
# PROJECT CONFIGURATION
# ============================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.extract import extract_all_locations, save_raw_data
from src.transform import transform_weather_data
from src.validate import validate_weather_data
from src.load import load_weather_data


RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# ============================================
# AIRFLOW DAG CONFIGURATION
# ============================================

@dag(
    dag_id="weather_etl_pipeline",
    description="Daily Open-Meteo weather ETL pipeline",

    # Execute once per day
    schedule="@daily",

    # South African timezone
    start_date=pendulum.datetime(
        2026,
        6,
        1,
        tz="Africa/Johannesburg",
    ),

    # Do not backfill old schedules automatically
    catchup=False,

    # Prevent overlapping DAG runs
    max_active_runs=1,

    # Retry failed tasks
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },

    tags=[
        "weather",
        "etl",
        "data-engineering",
        "capstone",
    ],
)
def weather_etl_pipeline():
    """
    Orchestrate the daily weather ETL workflow.

    Workflow:
        Extract
        -> Transform
        -> Validate
        -> Load
    """

    # ========================================
    # TASK 1: EXTRACT
    # ========================================

    @task
    def extract_weather() -> str:
        """Extract weather data from Open-Meteo."""

        logging.info(
            "Starting weather data extraction."
        )

        raw_data = extract_all_locations()

        if not raw_data:
            raise ValueError(
                "Extraction failed: no weather data returned."
            )

        raw_file_path = save_raw_data(raw_data)

        logging.info(
            "Weather extraction completed. File: %s",
            raw_file_path,
        )

        return str(Path(raw_file_path).resolve())

    # ========================================
    # TASK 2: TRANSFORM
    # ========================================

    @task
    def transform_weather(raw_file_path: str) -> str:
        """Transform nested JSON into structured data."""

        logging.info(
            "Starting weather transformation."
        )

        with open(
            raw_file_path,
            mode="r",
            encoding="utf-8",
        ) as file:
            raw_data = json.load(file)

        transformed_data = transform_weather_data(
            raw_data
        )

        if transformed_data.empty:
            raise ValueError(
                "Transformation produced an empty DataFrame."
            )

        output_path = (
            PROCESSED_DIR / "weather_transformed.csv"
        )

        transformed_data.to_csv(
            output_path,
            index=False,
        )

        logging.info(
            "Transformation completed. Rows: %s",
            len(transformed_data),
        )

        return str(output_path.resolve())

    # ========================================
    # TASK 3: VALIDATE
    # ========================================

    @task
    def validate_weather(
        transformed_file_path: str,
    ) -> str:
        """Validate transformed weather records."""

        logging.info(
            "Starting weather data validation."
        )

        transformed_data = pd.read_csv(
            transformed_file_path,
            parse_dates=["observation_date"],
        )

        if transformed_data.empty:
            raise ValueError(
                "Validation failed: empty dataset."
            )

        validate_weather_data(
            transformed_data
        )

        logging.info(
            "Validation completed. Rows checked: %s",
            len(transformed_data),
        )

        return transformed_file_path

    # ========================================
    # TASK 4: LOAD
    # ========================================

    @task
    def load_weather(
        validated_file_path: str,
    ) -> str:
        """Load validated weather data into SQLite."""

        logging.info(
            "Starting weather data warehouse load."
        )

        validated_data = pd.read_csv(
            validated_file_path,
            parse_dates=["observation_date"],
        )

        database_path = load_weather_data(
            validated_data
        )

        logging.info(
            "Weather data loaded successfully."
        )

        logging.info(
            "Database location: %s",
            database_path,
        )

        return str(database_path)

    # ========================================
    # TASK DEPENDENCIES
    # ========================================

    raw_file = extract_weather()

    transformed_file = transform_weather(
        raw_file
    )

    validated_file = validate_weather(
        transformed_file
    )

    load_weather(
        validated_file
    )


# Register the DAG with Apache Airflow
weather_etl_pipeline()
