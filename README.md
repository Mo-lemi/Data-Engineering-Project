# SA Weather ETL

A small ETL pipeline that downloads daily historical weather data for five South African cities, cleans it with pandas, loads it into a SQLite database, and answers a few questions with SQL.

> Status: in development.

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
- **Raw data is not committed.** Downloaded CSVs and the database are generated files and can always be recreated by running the pipeline, so `.gitignore` excludes them.
