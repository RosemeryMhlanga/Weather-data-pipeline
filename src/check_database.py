
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd


# ==========================================
# 1. DATABASE CONFIGURATION
# ==========================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATABASE_PATH = PROJECT_ROOT / "data" / "weather.db"

if not DATABASE_PATH.is_file():
    raise FileNotFoundError(
        f"Weather database not found: {DATABASE_PATH}"
    )


# ==========================================
# 2. DYNAMIC FORECAST DATE RANGE
# ==========================================

# Use South African local time
south_africa_tz = ZoneInfo("Africa/Johannesburg")

today = datetime.now(south_africa_tz).date()

# Today plus the next 6 days = 7 days
end_date = today + timedelta(days=6)


# ==========================================
# 3. CONNECT TO SQLITE DATABASE
# ==========================================

connection = sqlite3.connect(DATABASE_PATH)

try:

    # ======================================
    # 4. DATABASE RECORD COUNTS
    # ======================================

    tables = [
        "dim_location",
        "dim_date",
        "fact_weather",
        "staging_weather_raw",
    ]

    print("\nWEATHER DATA WAREHOUSE VALIDATION")
    print("=" * 65)

    for table in tables:
        query = f"SELECT COUNT(*) FROM {table}"

        count = connection.execute(query).fetchone()[0]

        print(f"{table}: {count} rows")

    # ======================================
    # 5. DISPLAY FORECAST DATE RANGE
    # ======================================

    print("\nCURRENT 7-DAY WEATHER FORECAST")
    print("=" * 105)

    print(f"Forecast start date: {today}")
    print(f"Forecast end date:   {end_date}")

    # ======================================
    # 6. RETRIEVE ACTUAL WEATHER DATA
    # ======================================

    query = """
    SELECT
        l.location_name AS City,
        d.full_date AS Forecast_Date,
        f.temperature_max AS Max_Temperature,
        f.temperature_min AS Min_Temperature,
        f.average_temperature AS Avg_Temperature,
        f.precipitation AS Precipitation,
        f.wind_speed_max AS Wind_Speed

    FROM fact_weather AS f

    INNER JOIN dim_location AS l
        ON f.location_id = l.location_id

    INNER JOIN dim_date AS d
        ON f.date_id = d.date_id

    WHERE d.full_date BETWEEN ? AND ?

    ORDER BY
        d.full_date ASC,
        l.location_name ASC
    """

    weather_data = pd.read_sql_query(
        query,
        connection,
        params=(
            today.isoformat(),
            end_date.isoformat(),
        ),
    )

    # ======================================
    # 7. DISPLAY WEATHER MEASUREMENTS
    # ======================================

    if weather_data.empty:
        print("\nNo forecast records found.")
        print("Run the ETL pipeline to refresh weather data.")

    else:
        print("\nACTUAL WEATHER MEASUREMENTS")
        print("-" * 105)

        print(
            weather_data.to_string(
                index=False,
            )
        )

        # ==================================
        # 8. FORECAST VALIDATION SUMMARY
        # ==================================

        print("\nFORECAST VALIDATION SUMMARY")
        print("-" * 65)

        total_records = len(weather_data)

        total_cities = weather_data["City"].nunique()

        total_days = weather_data["Forecast_Date"].nunique()

        expected_records = 3 * 7

        print(f"Total forecast records: {total_records}")

        print(f"Total cities: {total_cities}")

        print(f"Total forecast days: {total_days}")

        print(f"Expected records: {expected_records}")

        duplicate_count = weather_data.duplicated(
            subset=["City", "Forecast_Date"]
        ).sum()

        print(f"Duplicate city/date rows: {duplicate_count}")

        if (
            total_records == expected_records
            and total_cities == 3
            and total_days == 7
            and duplicate_count == 0
        ):
            print("\nForecast record-count checks PASSED.")

        else:
            print("\nForecast record-count checks need review.")

finally:
    # ======================================
    # 9. CLOSE DATABASE CONNECTION
    # ======================================

    connection.close()
