import pandas as pd

from src.transform import transform_weather_data


def create_sample_raw_data() -> list[dict]:
    """Create controlled sample API data for testing."""

    return [
        {
            "location_name": "pretoria",
            "requested_latitude": -25.7479,
            "requested_longitude": 28.2293,
            "api_response": {
                "daily": {
                    "time": [
                        "2026-06-24",
                        "2026-06-25",
                    ],
                    "weather_code": [
                        1,
                        3,
                    ],
                    "temperature_2m_max": [
                        20.0,
                        22.0,
                    ],
                    "temperature_2m_min": [
                        10.0,
                        12.0,
                    ],
                    "precipitation_sum": [
                        0.0,
                        2.5,
                    ],
                    "wind_speed_10m_max": [
                        15.0,
                        18.0,
                    ],
                }
            },
        }
    ]


def test_transform_returns_dataframe() -> None:
    """Check that transformation returns a pandas DataFrame."""

    raw_data = create_sample_raw_data()

    result = transform_weather_data(raw_data)

    assert isinstance(result, pd.DataFrame)


def test_transform_creates_correct_number_of_rows() -> None:
    """Check that one row is created for every weather date."""

    raw_data = create_sample_raw_data()

    result = transform_weather_data(raw_data)

    assert len(result) == 2


def test_location_name_is_standardized() -> None:
    """Check that location names are standardized."""

    raw_data = create_sample_raw_data()

    result = transform_weather_data(raw_data)

    assert result.loc[0, "location_name"] == "Pretoria"


def test_average_temperature_is_calculated() -> None:
    """Check the derived average temperature field."""

    raw_data = create_sample_raw_data()

    result = transform_weather_data(raw_data)

    assert result.loc[0, "average_temperature"] == 15.0


def test_observation_date_is_datetime() -> None:
    """Check that observation dates are converted to datetime."""

    raw_data = create_sample_raw_data()

    result = transform_weather_data(raw_data)

    assert pd.api.types.is_datetime64_any_dtype(
        result["observation_date"]
    )