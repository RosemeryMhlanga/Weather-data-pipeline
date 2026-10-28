import logging

from src.etl import run_etl_pipeline
from src.elt import run_elt_pipeline


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def main() -> None:
    """Run and test both ETL and ELT workflows."""

    print("\n--------------------------------")
    print("RUNNING ETL WORKFLOW")
    print("--------------------------------")

    etl_database = run_etl_pipeline()

    print("\nETL completed successfully.")
    print(f"ETL database: {etl_database}")

    print("\n--------------------------------")
    print("RUNNING ELT WORKFLOW")
    print("--------------------------------")

    elt_database = run_elt_pipeline()

    print("\nELT completed successfully.")
    print(f"ELT database: {elt_database}")

    print("\nBoth workflows completed successfully.")


if __name__ == "__main__":
    main()