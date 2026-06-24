PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS dim_location (
    location_id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_name TEXT NOT NULL UNIQUE,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_id INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    day INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name TEXT NOT NULL,
    year INTEGER NOT NULL,
    day_of_week TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_weather (
    weather_id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id INTEGER NOT NULL,
    date_id INTEGER NOT NULL,
    weather_code INTEGER,
    temperature_max REAL,
    temperature_min REAL,
    average_temperature REAL,
    precipitation REAL,
    wind_speed_max REAL,

    FOREIGN KEY (location_id)
        REFERENCES dim_location(location_id),

    FOREIGN KEY (date_id)
        REFERENCES dim_date(date_id),

    UNIQUE (location_id, date_id)
);
