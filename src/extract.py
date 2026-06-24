import json
import logging
from pathlib import Path

import requests


API_URL = "https://api.open-meteo.com/v1/forecast"

LOCATIONS = [
    {
        "name": "Pretoria",
        "latitude": -25.7479,
        "longitude": 28.2293,
    },
    {
        "name": "Johannesburg",
        "latitude": -26.2041,
        "longitude": 28.0473,
    },
    {
        "name": "Cape Town",
        "latitude": -33.9249,
        "longitude": 18.4241,
    },
]


def extract_weather_data(location: dict) -> dict:
    """
    Extract daily weather forecast data for one location.

    Args:
        location: Dictionary containing the location name,
                  latitude and longitude.

    Returns:
        Dictionary containing the location details and API response.
    """

    parameters = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "daily": [
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "wind_speed_10m_max",
        ],
        "timezone": "Africa/Johannesburg",
        "forecast_days": 7,
    }

    try:
        response = requests.get(
            API_URL,
            params=parameters,
            timeout=30,
        )

        response.raise_for_status()

        weather_data = response.json()

        if "daily" not in weather_data:
            raise ValueError(
                f"Daily weather data is missing for {location['name']}."
            )

        logging.info(
            "Weather data extracted successfully for %s.",
            location["name"],
        )

        return {
            "location_name": location["name"],
            "requested_latitude": location["latitude"],
            "requested_longitude": location["longitude"],
            "api_response": weather_data,
        }

    except requests.RequestException as error:
        logging.error(
            "API request failed for %s: %s",
            location["name"],
            error,
        )
        raise

    except ValueError as error:
        logging.error(
            "Invalid API response for %s: %s",
            location["name"],
            error,
        )
        raise


def extract_all_locations() -> list[dict]:
    """
    Extract weather data for all configured locations.
    """

    extracted_data = []

    for location in LOCATIONS:
        weather_data = extract_weather_data(location)
        extracted_data.append(weather_data)

    return extracted_data


def save_raw_data(data: list[dict]) -> Path:
    """
    Save raw API data as a JSON file.
    """

    output_path = Path("data/raw/weather_raw.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open(
        mode="w",
        encoding="utf-8",
    ) as file:
        json.dump(data, file, indent=4)

    logging.info("Raw weather data saved to %s.", output_path)

    return output_path
    