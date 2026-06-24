import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path

from src.extract import extract_all_locations
from src.load import DATABASE_PATH, load_weather_data
from src.transform import transform_weather_data
from src.validate import validate_weather_data


def create_staging_table() -> None:
    """Create the table used to store raw API data."""

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
            "Staging table created successfully."
        )

    except sqlite3.Error as error:
        logging.error(
            "Staging table creation failed: %s",
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

            # Remove the previous staging batch
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
            "Raw weather data loaded into staging."
        )

    except sqlite3.Error as error:
        logging.error(
            "Loading raw staging data failed: %s",
            error,
        )
        raise


def read_staged_data() -> list[dict]:
    """Read and convert staged JSON back to Python dictionaries."""

    try:
        with sqlite3.connect(DATABASE_PATH) as connection:
            rows = connection.execute(
                """
                SELECT raw_json
                FROM staging_weather_raw
                ORDER BY staging_id;
                """
            ).fetchall()

        staged_data = [
            json.loads(row[0])
            for row in rows
        ]

        if not staged_data:
            raise ValueError(
                "No raw weather data was found in staging."
            )

        logging.info(
            "Raw weather data read from staging."
        )

        return staged_data

    except sqlite3.Error as error:
        logging.error(
            "Reading staged weather data failed: %s",
            error,
        )
        raise


def run_elt_pipeline() -> Path:
    """
    Run the complete ELT workflow.

    ELT means:
    Extract → Load raw → Transform → Validate → Load final tables
    """

    logging.info("Weather ELT pipeline started.")

    # 1. Extract data from the API
    raw_data = extract_all_locations()

    # 2. Load raw data into the staging table
    load_raw_data_to_staging(raw_data)

    # 3. Read the raw data from staging
    staged_data = read_staged_data()

    # 4. Transform the staged data
    transformed_data = transform_weather_data(
        staged_data
    )

    # 5. Validate the transformed data
    validation_passed = validate_weather_data(
        transformed_data
    )

    if not validation_passed:
        raise ValueError(
            "ELT weather data validation failed."
        )

    # 6. Load clean data into final star-schema tables
    database_path = load_weather_data(
        transformed_data
    )

    logging.info(
        "Weather ELT pipeline completed successfully."
    )

    return database_path