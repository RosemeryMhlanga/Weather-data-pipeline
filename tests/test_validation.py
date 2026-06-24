import pandas as pd
import pytest

from src.validate import validate_weather_data


def create_valid_dataframe() -> pd.DataFrame:
    """Create a valid weather DataFrame for testing."""

    return pd.DataFrame(
        {
            "location_name": [
                "Pretoria",
                "Pretoria",
            ],
            "latitude": [
                -25.7479,
                -25.7479,
            ],
            "longitude": [
                28.2293,
                28.2293,
            ],
            "observation_date": pd.to_datetime(
                [
                    "2026-06-24",
                    "2026-06-25",
                ]
            ),
            "weather_code": [
                1,
                3,
            ],
            "temperature_max": [
                20.0,
                22.0,
            ],
            "temperature_min": [
                10.0,
                12.0,
            ],
            "average_temperature": [
                15.0,
                17.0,
            ],
            "precipitation": [
                0.0,
                2.5,
            ],
            "wind_speed_max": [
                15.0,
                18.0,
            ],
        }
    )


def test_valid_weather_data_passes() -> None:
    """Check that valid weather data passes validation."""

    dataframe = create_valid_dataframe()

    result = validate_weather_data(dataframe)

    assert result is True


def test_empty_dataframe_fails() -> None:
    """Check that an empty DataFrame fails validation."""

    dataframe = pd.DataFrame()

    with pytest.raises(
        ValueError,
        match="DataFrame is empty",
    ):
        validate_weather_data(dataframe)


def test_missing_required_column_fails() -> None:
    """Check that missing required columns fail validation."""

    dataframe = create_valid_dataframe()

    dataframe = dataframe.drop(
        columns=["precipitation"]
    )

    with pytest.raises(
        ValueError,
        match="Required columns are missing",
    ):
        validate_weather_data(dataframe)


def test_missing_value_fails() -> None:
    """Check that missing required values fail validation."""

    dataframe = create_valid_dataframe()

    dataframe.loc[0, "temperature_max"] = None

    with pytest.raises(
        ValueError,
        match="Missing values were found",
    ):
        validate_weather_data(dataframe)


def test_duplicate_record_fails() -> None:
    """Check that duplicate location-date records fail."""

    dataframe = create_valid_dataframe()

    duplicate_row = dataframe.iloc[[0]]

    dataframe = pd.concat(
        [
            dataframe,
            duplicate_row,
        ],
        ignore_index=True,
    )

    with pytest.raises(
        ValueError,
        match="Duplicate location and date records",
    ):
        validate_weather_data(dataframe)


def test_invalid_temperature_range_fails() -> None:
    """Check that minimum temperature cannot exceed maximum."""

    dataframe = create_valid_dataframe()

    dataframe.loc[0, "temperature_min"] = 30.0

    with pytest.raises(
        ValueError,
        match="minimum temperature is higher",
    ):
        validate_weather_data(dataframe)


def test_negative_precipitation_fails() -> None:
    """Check that precipitation cannot be negative."""

    dataframe = create_valid_dataframe()

    dataframe.loc[0, "precipitation"] = -1.0

    with pytest.raises(
        ValueError,
        match="Precipitation cannot be negative",
    ):
        validate_weather_data(dataframe)


def test_negative_wind_speed_fails() -> None:
    """Check that wind speed cannot be negative."""

    dataframe = create_valid_dataframe()

    dataframe.loc[0, "wind_speed_max"] = -5.0

    with pytest.raises(
        ValueError,
        match="Wind speed cannot be negative",
    ):
        validate_weather_data(dataframe)