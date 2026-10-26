# SA Weather ETL

A small ETL pipeline that downloads daily historical weather data for five South African cities, cleans it with pandas, loads it into a SQLite database, and answers a few questions with SQL.

> Status: Complete.

Verification code: WTC-6RAQMRKQ

## Demo video

https://youtu.be/4ZBasPoD8vI

## Data source

[Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api): free, no API key, returns CSV.

- Cities: Johannesburg, Pretoria, Cape Town, Durban, Bloemfontein
- Period: 2020-01-01 to 2024-12-31
- Daily fields: max temperature, min temperature, precipitation, max wind speed

## Architecture

```
Open-Meteo CSV ──► extract ──► data/raw/*.csv ──► transform ──► load ──► weather.db (SQLite) ──► SQL queries
```

## How to run

Requires Python 3.11+ (the minimum for pandas 3).

```
pip install -r requirements.txt
python pipeline.py        # downloads, cleans and loads everything into weather.db
python run_queries.py     # answers the five questions below
python -m pytest          # runs the cleaning-rule tests
```

Running the pipeline again is safe: it refreshes the data without creating duplicates.

## Project structure

```
config.py              cities, date range, file paths
pipeline.py            runs extract -> transform -> load
run_queries.py         runs sql/queries.sql and prints the results
src/extract.py         downloads one CSV per city from Open-Meteo
src/transform.py       reads, renames and cleans the raw CSVs
src/load.py            creates the database and upserts the data
sql/schema.sql         table definitions
sql/queries.sql        the five analysis queries
tests/test_transform.py  tests for the cleaning rules
```

## Database schema

```
cities                         daily_weather
------------------------       ------------------------------
city_id    PK                  city_id          PK, FK -> cities
name       UNIQUE              date             PK (YYYY-MM-DD)
province                       temp_max_c
latitude                       temp_min_c
longitude                      precipitation_mm
                               wind_max_kmh
```

5 cities × 1,827 days = 9,135 rows in `daily_weather`.

## Results

**Q1. Warmest city on average** (daily mean = average of max and min)

| City | Avg temp (°C) |
|---|---|
| Durban | 20.8 |
| Pretoria | 18.4 |
| Cape Town | 17.2 |
| Bloemfontein | 16.8 |
| Johannesburg | 16.3 |

Johannesburg is the coolest despite being further north, mainly because it sits about 1,750 m above sea level.

**Q2. Wettest month per city** (average rainfall for that month over 5 years)

| City | Month | Avg rain (mm) |
|---|---|---|
| Bloemfontein | January | 92.9 |
| Cape Town | June | 144.7 |
| Durban | December | 120.6 |
| Johannesburg | December | 127.0 |
| Pretoria | December | 116.1 |

Cape Town has winter rainfall. The other four cities get most of their rain from summer thunderstorms.

**Q3. Days above 30 °C per year**

| City | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|
| Bloemfontein | 51 | 26 | 25 | 65 | 98 |
| Cape Town | 11 | 8 | 13 | 12 | 29 |
| Durban | 31 | 26 | 8 | 28 | 37 |
| Johannesburg | 6 | 5 | 5 | 18 | 33 |
| Pretoria | 27 | 35 | 25 | 69 | 93 |

**Q4. Average gap between day and night temperature**

| City | Avg range (°C) |
|---|---|
| Bloemfontein | 14.0 |
| Pretoria | 12.8 |
| Johannesburg | 12.5 |
| Durban | 8.3 |
| Cape Town | 7.7 |

The coastal cities have the smallest gap because the ocean keeps their temperature steady.

**Q5. Average temperature across all five cities per year**

| Year | Avg temp (°C) |
|---|---|
| 2020 | 17.73 |
| 2021 | 17.57 |
| 2022 | 17.71 |
| 2023 | 17.95 |
| 2024 | 18.67 |

2024 was clearly the warmest year, but five years is too short to call this a long-term trend.

## Design decisions

- **Settings in one place (`config.py`).** Cities, coordinates and the date range live in one file, so changing what the pipeline fetches never means editing the pipeline code.
- **Extract saves files unchanged.** The extract step only downloads and saves. All cleaning happens in transform, so if a cleaning rule is wrong it can be fixed and re-run without downloading again. (Open-Meteo snaps each city to the nearest point on its weather grid, so the stored coordinates differ slightly from those in `config.py`.)
- **Cleaning removes bad rows instead of fixing them.** Transform drops duplicate days, days with any missing measurement, and impossible values (min temperature above max, negative rain or wind). Guessing a replacement value would invent data. Removing a few rows from about 1,800 per city barely affects averages. The current data has none of these problems, but the rules protect future downloads, and `tests/test_transform.py` proves each rule works.
- **Two normalised tables.** `cities` holds each city's details once, and `daily_weather` refers to it by `city_id` (a foreign key). This avoids repeating the name, province and coordinates on about 1,800 rows per city. The primary key `(city_id, date)` makes the database itself refuse a second row for the same city and day.
- **Loading is safe to repeat.** The schema uses `CREATE TABLE IF NOT EXISTS`, and both tables are loaded with an upsert (`INSERT ... ON CONFLICT DO UPDATE`). Running the pipeline twice therefore gives the same result as running it once, each city keeps its `city_id`, and corrected values from a new download replace the old ones.
- **Foreign keys switched on.** SQLite ignores `REFERENCES` constraints unless `PRAGMA foreign_keys = ON` is set on each connection, so `connect()` in `src/load.py` always sets it.
- **SQL lives in `.sql` files.** The schema and the analysis queries are plain SQL files rather than strings hidden inside Python, so they can be read, reviewed and run on their own.
- **Raw data is not committed.** Downloaded CSVs and the database are generated files and can always be recreated by running the pipeline, so `.gitignore` excludes them.
- **Right-sized tools.** About 9,000 rows fit easily on one machine, so the pipeline uses plain Python, pandas and SQLite. Airflow, Spark, Kafka and Docker were left out on purpose: they solve problems of scale and scheduling that this project doesn't have, and would make it harder to run and explain. If the data grew or needed a daily schedule, those would be the next steps.
