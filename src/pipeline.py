import logging
from pathlib import Path

import pandas as pd

from src.extract import extract_all_locations, save_raw_data
from src.transform import transform_weather_data
from src.validate import validate_weather_data
from src.load import load_weather_data


class WeatherPipeline:
    """Run the complete weather ETL pipeline."""

    def __init__(self) -> None:
        """Initialize pipeline result variables."""

        self.raw_data: list[dict] = []
        self.transformed_data = pd.DataFrame()
        self.raw_file_path: Path | None = None
        self.database_path: Path | None = None

    def extract(self) -> list[dict]:
        """Extract weather data from the API."""

        logging.info("Pipeline extract stage started.")

        self.raw_data = extract_all_locations()
        self.raw_file_path = save_raw_data(self.raw_data)

        logging.info("Pipeline extract stage completed.")

        return self.raw_data

    def transform(self) -> pd.DataFrame:
        """Transform the extracted weather data."""

        logging.info("Pipeline transform stage started.")

        if not self.raw_data:
            raise ValueError(
                "No raw data is available. Run extract first."
            )

        self.transformed_data = transform_weather_data(
            self.raw_data
        )

        logging.info("Pipeline transform stage completed.")

        return self.transformed_data

    def validate(self) -> bool:
        """Validate the transformed weather data."""

        logging.info("Pipeline validation stage started.")

        if self.transformed_data.empty:
            raise ValueError(
                "No transformed data is available. "
                "Run transform first."
            )

        validation_passed = validate_weather_data(
            self.transformed_data
        )

        logging.info("Pipeline validation stage completed.")

        return validation_passed

    def load(self) -> Path:
        """Load the validated data into SQLite."""

        logging.info("Pipeline load stage started.")

        if self.transformed_data.empty:
            raise ValueError(
                "No transformed data is available. "
                "Run transform first."
            )

        self.database_path = load_weather_data(
            self.transformed_data
        )

        logging.info("Pipeline load stage completed.")

        return self.database_path

    def run(self) -> None:
        """Run extract, transform, validate, and load."""

        logging.info("Weather pipeline class started.")

        self.extract()
        self.transform()
        validation_passed = self.validate()
        self.load()

        logging.info(
            "Weather pipeline class completed successfully."
        )

        print("\nPipeline completed successfully.")
        print(f"Raw file: {self.raw_file_path}")
        print(f"Validation passed: {validation_passed}")
        print(f"Database: {self.database_path}")