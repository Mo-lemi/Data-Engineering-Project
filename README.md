# SA Weather ETL

A small ETL pipeline that downloads daily historical weather data for five South African cities, cleans it with pandas, loads it into a SQLite database, and answers a few questions with SQL.

> Status: in development.

Verification code: WTC-6RAQMRKQ

## Demo video

_Coming soon._

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

_Coming soon._

## Design decisions

- **Settings in one place (`config.py`).** Cities, coordinates and the date range live in one file, so changing what the pipeline fetches never means editing the pipeline code.
- **Extract saves files unchanged.** The extract step only downloads and saves. All cleaning happens in transform, so if a cleaning rule is wrong it can be fixed and re-run without downloading again. (Open-Meteo snaps each city to the nearest point on its weather grid, so the stored coordinates differ slightly from those in `config.py`.)
- **Cleaning removes bad rows instead of fixing them.** Transform drops duplicate days, days with any missing measurement, and impossible values (min temperature above max, negative rain or wind). Guessing a replacement value would invent data. Removing a few rows from about 1,800 per city barely affects averages. The current data has none of these problems, but the rules protect future downloads, and `tests/test_transform.py` proves each rule works.
- **Two normalised tables.** `cities` holds each city's details once, and `daily_weather` refers to it by `city_id` (a foreign key). This avoids repeating the name, province and coordinates on about 1,800 rows per city. The primary key `(city_id, date)` makes the database itself refuse a second row for the same city and day.
- **Loading is safe to repeat.** The schema uses `CREATE TABLE IF NOT EXISTS`, and cities are loaded with an upsert (`INSERT ... ON CONFLICT DO UPDATE`). Running the pipeline twice therefore gives the same result as running it once, and each city keeps its `city_id`.
- **Raw data is not committed.** Downloaded CSVs and the database are generated files and can always be recreated by running the pipeline, so `.gitignore` excludes them.
