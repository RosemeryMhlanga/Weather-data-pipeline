import json
import os
import sys
from pathlib import Path

import pandas as pd
import pendulum
from airflow.decorators import dag, task


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from src.extract import extract_all_locations, save_raw_data
from src.load import load_weather_data
from src.transform import transform_weather_data
from src.validate import validate_weather_data


@dag(
    dag_id="weather_etl_pipeline",
    description="Daily Open-Meteo weather ETL pipeline",
    schedule="@daily",
    start_date=pendulum.datetime(
        2026,
        6,
        1,
        tz="Africa/Johannesburg",
    ),
    catchup=False,
    tags=["weather", "etl", "capstone"],
)
def weather_etl_pipeline():
    """Extract, transform, validate, and load weather data."""

    @task
    def extract_weather() -> str:
        """Extract API data and save it as raw JSON."""

        os.chdir(PROJECT_ROOT)

        raw_data = extract_all_locations()
        raw_file_path = save_raw_data(raw_data)

        return str(raw_file_path)

    @task
    def transform_weather(raw_file_path: str) -> str:
        """Transform raw JSON into a clean CSV file."""

        os.chdir(PROJECT_ROOT)

        with open(
            raw_file_path,
            mode="r",
            encoding="utf-8",
        ) as file:
            raw_data = json.load(file)

        transformed_data = transform_weather_data(raw_data)

        output_path = Path(
            "data/processed/weather_transformed.csv"
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        transformed_data.to_csv(
            output_path,
            index=False,
        )

        return str(output_path)

    @task
    def validate_weather(
        transformed_file_path: str,
    ) -> str:
        """Validate the transformed weather CSV."""

        os.chdir(PROJECT_ROOT)

        transformed_data = pd.read_csv(
            transformed_file_path,
            parse_dates=["observation_date"],
        )

        validate_weather_data(transformed_data)

        return transformed_file_path

    @task
    def load_weather(
        validated_file_path: str,
    ) -> str:
        """Load validated data into the SQLite star schema."""

        os.chdir(PROJECT_ROOT)

        validated_data = pd.read_csv(
            validated_file_path,
            parse_dates=["observation_date"],
        )

        database_path = load_weather_data(
            validated_data
        )

        return str(database_path)

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


weather_etl_pipeline()