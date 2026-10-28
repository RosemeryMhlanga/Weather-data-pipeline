
import sqlite3

connection = sqlite3.connect("data/weather.db")
cursor = connection.cursor()

tables = [
    "dim_location",
    "dim_date",
    "fact_weather",
    "staging_weather_raw"
]

print("WEATHER DATA WAREHOUSE VALIDATION")
print("-" * 40)

for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"{table}: {count} rows")

connection.close()
