import logging

import pandas as pd


REQUIRED_COLUMNS = [
    "location_name",
    "latitude",
    "longitude",
    "observation_date",
    "weather_code",
    "temperature_max",
    "temperature_min",
    "average_temperature",
    "precipitation",
    "wind_speed_max",
]


def validate_weather_data(dataframe: pd.DataFrame) -> bool:
    """
    Validate the transformed weather DataFrame.

    Args:
        dataframe: Transformed weather data.

    Returns:
        True when all validation checks pass.

    Raises:
        ValueError: If any validation check fails.
    """

    if dataframe.empty:
        raise ValueError("The transformed weather DataFrame is empty.")

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in dataframe.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Required columns are missing: {missing_columns}"
        )

    if dataframe[REQUIRED_COLUMNS].isnull().any().any():
        raise ValueError(
            "Missing values were found in required columns."
        )

    if dataframe.duplicated(
        subset=["location_name", "observation_date"]
    ).any():
        raise ValueError(
            "Duplicate location and date records were found."
        )

    if (
        dataframe["temperature_min"]
        > dataframe["temperature_max"]
    ).any():
        raise ValueError(
            "A minimum temperature is higher than a maximum temperature."
        )

    if (dataframe["precipitation"] < 0).any():
        raise ValueError(
            "Precipitation cannot be negative."
        )

    if (dataframe["wind_speed_max"] < 0).any():
        raise ValueError(
            "Wind speed cannot be negative."
        )

    if not pd.api.types.is_datetime64_any_dtype(
        dataframe["observation_date"]
    ):
        raise ValueError(
            "observation_date is not a proper datetime column."
        )

    logging.info(
        "Weather data validation passed. Rows checked: %s",
        len(dataframe),
    )

    return True