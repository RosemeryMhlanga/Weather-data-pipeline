import logging
import sqlite3
from pathlib import Path

import pandas as pd


DATABASE_PATH = Path("data/weather.db")
SCHEMA_PATH = Path("sql/schema.sql")


def create_database() -> None:
    """Create the SQLite database and star-schema tables."""

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    schema_sql = SCHEMA_PATH.read_text(
        encoding="utf-8"
    )

    try:
        with sqlite3.connect(DATABASE_PATH) as connection:
            connection.execute("PRAGMA foreign_keys = ON;")
            connection.executescript(schema_sql)
            connection.commit()

        logging.info(
            "Database and tables created successfully."
        )

    except sqlite3.Error as error:
        logging.error(
            "Database creation failed: %s",
            error,
        )
        raise


def load_locations(
    connection: sqlite3.Connection,
    dataframe: pd.DataFrame,
) -> None:
    """Load unique locations into dim_location."""

    locations = dataframe[
        [
            "location_name",
            "latitude",
            "longitude",
        ]
    ].drop_duplicates()

    for row in locations.itertuples(index=False):
        connection.execute(
            """
            INSERT INTO dim_location (
                location_name,
                latitude,
                longitude
            )
            VALUES (?, ?, ?)
            ON CONFLICT(location_name)
            DO UPDATE SET
                latitude = excluded.latitude,
                longitude = excluded.longitude;
            """,
            (
                row.location_name,
                row.latitude,
                row.longitude,
            ),
        )

    logging.info(
        "Location dimension loaded successfully."
    )


def load_dates(
    connection: sqlite3.Connection,
    dataframe: pd.DataFrame,
) -> None:
    """Load unique dates into dim_date."""

    unique_dates = (
        dataframe["observation_date"]
        .drop_duplicates()
        .sort_values()
    )

    for observation_date in unique_dates:
        date_id = int(
            observation_date.strftime("%Y%m%d")
        )

        connection.execute(
            """
            INSERT INTO dim_date (
                date_id,
                full_date,
                day,
                month,
                month_name,
                year,
                day_of_week
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(date_id)
            DO UPDATE SET
                full_date = excluded.full_date,
                day = excluded.day,
                month = excluded.month,
                month_name = excluded.month_name,
                year = excluded.year,
                day_of_week = excluded.day_of_week;
            """,
            (
                date_id,
                observation_date.strftime("%Y-%m-%d"),
                observation_date.day,
                observation_date.month,
                observation_date.strftime("%B"),
                observation_date.year,
                observation_date.strftime("%A"),
            ),
        )

    logging.info(
        "Date dimension loaded successfully."
    )


def load_weather_facts(
    connection: sqlite3.Connection,
    dataframe: pd.DataFrame,
) -> None:
    """Load weather measurements into fact_weather."""

    location_rows = connection.execute(
        """
        SELECT location_id, location_name
        FROM dim_location;
        """
    ).fetchall()

    location_ids = {
        location_name: location_id
        for location_id, location_name in location_rows
    }

    for row in dataframe.itertuples(index=False):
        location_id = location_ids[row.location_name]

        date_id = int(
            row.observation_date.strftime("%Y%m%d")
        )

        connection.execute(
            """
            INSERT INTO fact_weather (
                location_id,
                date_id,
                weather_code,
                temperature_max,
                temperature_min,
                average_temperature,
                precipitation,
                wind_speed_max
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(location_id, date_id)
            DO UPDATE SET
                weather_code = excluded.weather_code,
                temperature_max = excluded.temperature_max,
                temperature_min = excluded.temperature_min,
                average_temperature =
                    excluded.average_temperature,
                precipitation = excluded.precipitation,
                wind_speed_max = excluded.wind_speed_max;
            """,
            (
                location_id,
                date_id,
                row.weather_code,
                row.temperature_max,
                row.temperature_min,
                row.average_temperature,
                row.precipitation,
                row.wind_speed_max,
            ),
        )

    logging.info(
        "Weather fact table loaded successfully."
    )


def load_weather_data(
    dataframe: pd.DataFrame,
) -> Path:
    """Load transformed weather data into the star schema."""

    create_database()

    try:
        with sqlite3.connect(DATABASE_PATH) as connection:
            connection.execute(
                "PRAGMA foreign_keys = ON;"
            )

            load_locations(
                connection,
                dataframe,
            )

            load_dates(
                connection,
                dataframe,
            )

            load_weather_facts(
                connection,
                dataframe,
            )

            connection.commit()

        logging.info(
            "All weather data loaded successfully."
        )

        return DATABASE_PATH

    except sqlite3.Error as error:
        logging.error(
            "Weather data loading failed: %s",
            error,
        )
        raise