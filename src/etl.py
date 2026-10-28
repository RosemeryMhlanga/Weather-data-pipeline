import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.extract import extract_all_locations
from src.load import DATABASE_PATH, load_weather_data
from src.transform import transform_weather_data
from src.validate import validate_weather_data


def create_staging_table() -> None:
    """Create the raw weather staging table."""

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    try:
        with sqlite3.connect(DATABASE_PATH) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS staging_weather_raw (
                    staging_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    location_name TEXT NOT NULL,
                    raw_json TEXT NOT NULL,
                    loaded_at TEXT NOT NULL
                );
                """
            )

            connection.commit()

        logging.info(
            "Raw weather staging table created successfully."
        )

    except sqlite3.Error as error:
        logging.error(
            "Failed to create staging table: %s",
            error,
        )
        raise


def load_raw_data_to_staging(
    raw_data: list[dict],
) -> None:
    """Load raw API responses into the staging table."""

    create_staging_table()

    try:
        with sqlite3.connect(DATABASE_PATH) as connection:

            # Clear the previous staging batch
            connection.execute(
                """
                DELETE FROM staging_weather_raw;
                """
            )

            for location_data in raw_data:
                connection.execute(
                    """
                    INSERT INTO staging_weather_raw (
                        location_name,
                        raw_json,
                        loaded_at
                    )
                    VALUES (?, ?, ?);
                    """,
                    (
                        location_data["location_name"],
                        json.dumps(location_data),
                        datetime.now().isoformat(),
                    ),
                )

            connection.commit()

        logging.info(
            "Raw weather data loaded into staging successfully."
        )

    except sqlite3.Error as error:
        logging.error(
            "Failed to load raw data into staging: %s",
            error,
        )
        raise


def read_staged_data() -> list[dict]:
    """Read raw JSON records from the staging table."""

    try:
        with sqlite3.connect(DATABASE_PATH) as connection:
            staged_rows = connection.execute(
                """
                SELECT raw_json
                FROM staging_weather_raw
                ORDER BY staging_id;
                """
            ).fetchall()

        raw_data = [
            json.loads(row[0])
            for row in staged_rows
        ]

        if not raw_data:
            raise ValueError(
                "The staging table contains no raw weather data."
            )

        logging.info(
            "Raw weather data read from staging successfully."
        )

        return raw_data

    except sqlite3.Error as error:
        logging.error(
            "Failed to read staged data: %s",
            error,
        )
        raise

def run_etl_pipeline() -> Path:
    """Run the complete weather ETL workflow."""

    logging.info("Weather ETL pipeline started.")

    # 1. Extract weather data
    raw_data = extract_all_locations()

    # 2. Transform the extracted data
    transformed_data: pd.DataFrame = transform_weather_data(
        raw_data
    )

    # 3. Validate transformed data
    validate_weather_data(transformed_data)

    # 4. Load transformed data into final star-schema tables
    database_path = load_weather_data(
        transformed_data
    )

    logging.info(
        "Weather ETL pipeline completed successfully."
    )

    return database_path