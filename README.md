# Weather Data Engineering Pipeline

## Project Overview

This project implements a maintainable weather data pipeline using Python, the Open-Meteo API, pandas, SQL, and SQLite.

The pipeline extracts seven days of weather forecast data for Pretoria, Johannesburg, and Cape Town. It then transforms and validates the data before loading it into a SQLite database designed using a star schema.

The completed pipeline follows this process:

```text
Extract → Transform → Validate → Load
```

The project demonstrates data engineering and software engineering practices such as modular programming, data transformation, data validation, database design, logging, and exception handling.

## Technologies Used

* Python
* pandas
* requests
* SQLite
* SQL
* pytest
* Git
* GitHub
* Visual Studio Code

## Data Source

The weather data is retrieved from the Open-Meteo Weather API.

Open-Meteo provides weather forecast data without requiring an API key.

The pipeline retrieves the following information:

* Weather code
* Maximum temperature
* Minimum temperature
* Average temperature
* Precipitation
* Maximum wind speed
* Forecast date
* Location coordinates

## Locations

The pipeline extracts weather data for the following South African cities:

* Pretoria
* Johannesburg
* Cape Town

## Project Structure

```text
weather-data-pipeline/
│
├── data/
│   ├── raw/
│   │   └── weather_raw.json
│   └── weather.db
│
├── logs/
│
├── screenshots/
│
├── sql/
│   └── schema.sql
│
├── src/
│   ├── __init__.py
│   ├── extract.py
│   ├── transform.py
│   ├── validate.py
│   ├── load.py
│   └── pipeline.py
│
├── tests/
│   ├── __init__.py
│   ├── test_transform.py
│   └── test_validation.py
│
├── main.py
├── requirements.txt
├── README.md
└── .gitignore
```

## ETL Pipeline

### 1. Extract

The extraction stage connects to the Open-Meteo API using the Python `requests` library.

The extraction process:

* Sends a request to the Open-Meteo API
* Extracts seven days of weather data
* Extracts data for three locations
* Checks whether the API request was successful
* Checks whether the response contains daily weather data
* Handles API connection errors
* Logs successful and unsuccessful extraction events
* Saves the original API response as a JSON file

The raw API response is saved to:

```text
data/raw/weather_raw.json
```

The extraction code is stored in:

```text
src/extract.py
```

### 2. Transform

The transformation stage converts the nested JSON response into a clean pandas DataFrame.

The transformation process:

* Converts nested API data into rows and columns
* Creates one row for each city and forecast date
* Standardizes location names
* Converts the observation date into datetime format
* Converts weather measurements into numeric data types
* Removes duplicate city and date records
* Handles missing values in important fields
* Sorts the data by city and date
* Creates a derived average-temperature field
* Prepares the data for fact and dimension tables

Average temperature is calculated using:

```text
(maximum temperature + minimum temperature) / 2
```

The transformation code is stored in:

```text
src/transform.py
```

### 3. Validate

The validation stage checks the quality of the transformed data before it is loaded into the database.

The validation process checks that:

* The DataFrame is not empty
* All required columns are present
* Required columns do not contain missing values
* Duplicate city and date records do not exist
* Minimum temperature is not greater than maximum temperature
* Precipitation is not negative
* Wind speed is not negative
* Observation dates use the correct datetime data type

If any validation rule fails, the pipeline raises an error and stops before loading the data.

The validation code is stored in:

```text
src/validate.py
```

### 4. Load

The load stage saves the validated weather data into a SQLite database.

The database is saved to:

```text
data/weather.db
```

The load process:

* Creates the database directory when required
* Connects to SQLite
* Reads the SQL schema file
* Creates the database tables when they do not exist
* Loads unique cities into the location dimension
* Loads unique dates into the date dimension
* Loads weather measurements into the fact table
* Updates existing city and date records
* Prevents duplicate weather records
* Handles database connection and loading errors
* Logs successful loading events

The loading code is stored in:

```text
src/load.py
```

## Star Schema

The SQLite database uses a star schema.

The schema contains:

* One fact table
* Two dimension tables

The schema structure is:

```text
        dim_location
             |
             |
        fact_weather
             |
             |
          dim_date
```

### Location Dimension

The `dim_location` table stores information describing each location.

Columns:

* `location_id`
* `location_name`
* `latitude`
* `longitude`

Each city receives a unique `location_id`.

### Date Dimension

The `dim_date` table stores descriptive information about each forecast date.

Columns:

* `date_id`
* `full_date`
* `day`
* `month`
* `month_name`
* `year`
* `day_of_week`

The `date_id` uses the following format:

```text
YYYYMMDD
```

Example:

```text
20260624
```

### Weather Fact Table

The `fact_weather` table stores the weather measurements.

Columns:

* `weather_id`
* `location_id`
* `date_id`
* `weather_code`
* `temperature_max`
* `temperature_min`
* `average_temperature`
* `precipitation`
* `wind_speed_max`

The `location_id` connects the weather fact table to `dim_location`.

The `date_id` connects the weather fact table to `dim_date`.

The combination of `location_id` and `date_id` is unique. This prevents the same city's weather data from being inserted more than once for the same date.

The database schema is stored in:

```text
sql/schema.sql
```

## Installation

### 1. Open the project

Open the following folder in Visual Studio Code:

```text
weather-data-pipeline
```

### 2. Create a virtual environment

Run:

```powershell
python -m venv .venv
```

### 3. Activate the virtual environment

In Windows PowerShell, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\Activate.ps1
```

When the environment is active, the terminal should display:

```text
(.venv)
```

### 4. Install the required packages

Run:

```powershell
pip install -r requirements.txt
```

## Running the Pipeline

Run the complete ETL pipeline from the main project folder:

```powershell
python main.py
```

A successful pipeline run should:

1. Extract weather data from Open-Meteo
2. Save the raw JSON response
3. Transform the nested data into a DataFrame
4. Validate the transformed data
5. Create the SQLite database
6. Create the star-schema tables
7. Load the location dimension
8. Load the date dimension
9. Load the weather fact table

The terminal should show messages confirming that extraction, transformation, validation, and loading were successful.

## Expected Output

The pipeline creates the following outputs:

### Raw JSON file

```text
data/raw/weather_raw.json
```

### SQLite database

```text
data/weather.db
```

### Database tables

```text
dim_location
dim_date
fact_weather
```

For three cities and seven forecast days, the expected number of weather fact records is approximately:

```text
3 cities × 7 days = 21 weather records
```

## Logging and Error Handling

The project uses Python logging to record important pipeline events.

Logged events include:

* Pipeline start
* Successful API extraction
* Successful raw-data saving
* Successful transformation
* Successful validation
* Successful database creation
* Successful dimension-table loading
* Successful fact-table loading
* Pipeline completion
* API request failures
* Invalid API responses
* Validation failures
* Database errors

The current version displays logging messages in the terminal.

## Testing

The project includes a `tests` folder for pytest unit tests.

The planned tests cover:

* Transformation logic
* Required transformed columns
* Average-temperature calculation
* Missing-column validation
* Duplicate-record validation
* Invalid weather measurement validation

Tests can be run using:

```powershell
pytest
```

Only state that all tests passed after the test files have been completed and the command runs successfully.

## ELT Workflow

The project brief also requires a simple ELT workflow.

The planned ELT process is:

```text
Extract raw data
       ↓
Load raw data into a staging table
       ↓
Transform staged data
       ↓
Load final fact and dimension tables
```

The current working implementation focuses on the ETL process.

The ELT staging-table workflow remains an additional project component to be completed.

## Airflow Limitation

Apache Airflow automation was planned for this project.

However, the project was developed using native Windows, and the local Apache Airflow installation was unsuccessful. Apache Airflow is generally run in a Linux-based environment rather than directly as a standard native Windows application.

The completed pipeline can currently be executed manually using:

```powershell
python main.py
```

The working pipeline stages are:

```text
Extract → Transform → Validate → Load
```

Airflow automation could be added later using:

* Windows Subsystem for Linux 2
* Docker Desktop
* A Linux virtual machine
* A cloud-based Airflow environment

Airflow automation remains a known limitation and future enhancement of this project.

## Known Limitations

* Apache Airflow was not installed successfully in the native Windows environment
* The pipeline must currently be started manually
* The ELT staging workflow still needs to be completed
* Unit tests must be completed and run successfully
* The reusable class-based pipeline still needs to be completed

## Future Improvements

Future improvements may include:

* Running Apache Airflow through WSL2 or Docker
* Scheduling the pipeline to run daily
* Completing the ELT staging-table workflow
* Completing the reusable pipeline class
* Adding more South African locations
* Adding historical weather data
* Saving logs to a permanent log file
* Adding more unit tests
* Deploying the pipeline to a cloud platform

## Author

Rosemery Mhlanga

## Project Status

The core ETL pipeline is working successfully.

Completed components:

* API extraction
* Raw JSON storage
* Data transformation
* Data validation
* SQLite database creation
* Star-schema implementation
* Dimension-table loading
* Fact-table loading

Incomplete components:

* Apache Airflow automation
* ELT staging workflow
* Class-based pipeline
* Complete unit testing
* Permanent log-file output

This project was developed as part of the AICA Data Engineering Capstone Project.
