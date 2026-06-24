import logging

from src.pipeline import WeatherPipeline


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def main() -> None:
    """Run the complete class-based weather pipeline."""

    pipeline = WeatherPipeline()
    pipeline.run()


if __name__ == "__main__":
    main()