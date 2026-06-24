import logging

import pandas as pd


REQUIRED_DAILY_FIELDS = [
    "time",
    "weather_code",
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "wind_speed_10m_max",
]


def transform_weather_data(raw_data: list[dict]) -> pd.DataFrame:
    """
    Transform nested Open-Meteo responses into a clean DataFrame.

    Args:
        raw_data: List containing raw API responses for each location.

    Returns:
        A cleaned pandas DataFrame with one row per location per day.
    """

    records = []

    for location_data in raw_data:
        location_name = location_data["location_name"]
        latitude = location_data["requested_latitude"]
        longitude = location_data["requested_longitude"]

        daily_data = location_data["api_response"]["daily"]

        missing_fields = [
            field
            for field in REQUIRED_DAILY_FIELDS
            if field not in daily_data
        ]

        if missing_fields:
            raise ValueError(
                f"Missing daily fields for {location_name}: "
                f"{missing_fields}"
            )

        number_of_days = len(daily_data["time"])

        for index in range(number_of_days):
            record = {
                "location_name": location_name.strip().title(),
                "latitude": latitude,
                "longitude": longitude,
                "observation_date": daily_data["time"][index],
                "weather_code": daily_data["weather_code"][index],
                "temperature_max": daily_data[
                    "temperature_2m_max"
                ][index],
                "temperature_min": daily_data[
                    "temperature_2m_min"
                ][index],
                "precipitation": daily_data[
                    "precipitation_sum"
                ][index],
                "wind_speed_max": daily_data[
                    "wind_speed_10m_max"
                ][index],
            }

            records.append(record)

    dataframe = pd.DataFrame(records)

    dataframe["observation_date"] = pd.to_datetime(
        dataframe["observation_date"],
        errors="coerce",
    )

    numeric_columns = [
        "latitude",
        "longitude",
        "weather_code",
        "temperature_max",
        "temperature_min",
        "precipitation",
        "wind_speed_max",
    ]

    for column in numeric_columns:
        dataframe[column] = pd.to_numeric(
            dataframe[column],
            errors="coerce",
        )

    dataframe["average_temperature"] = (
        dataframe["temperature_max"]
        + dataframe["temperature_min"]
    ) / 2

    dataframe = dataframe.drop_duplicates(
        subset=["location_name", "observation_date"]
    )

    important_columns = [
        "location_name",
        "observation_date",
        "temperature_max",
        "temperature_min",
    ]

    dataframe = dataframe.dropna(
        subset=important_columns
    )

    dataframe = dataframe.sort_values(
        by=["location_name", "observation_date"]
    ).reset_index(drop=True)

    logging.info(
        "Weather data transformed successfully. Rows: %s",
        len(dataframe),
    )

    return dataframe