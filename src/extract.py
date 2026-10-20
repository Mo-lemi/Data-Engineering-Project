"""Extract step: download raw daily weather CSVs from Open-Meteo."""

import os

import requests

import config

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"


def download_city_csv(city):
    """Download one city's daily weather as CSV and save it unchanged to data/raw/."""
    params = {
        "latitude": city["latitude"],
        "longitude": city["longitude"],
        "start_date": config.START_DATE,
        "end_date": config.END_DATE,
        "daily": ",".join(config.DAILY_FIELDS),
        "timezone": config.TIMEZONE,
        "format": "csv",
    }
    response = requests.get(ARCHIVE_URL, params=params, timeout=60)
    # Stop with a clear error on a bad response instead of saving an error page as data.
    response.raise_for_status()

    os.makedirs(config.RAW_DATA_DIR, exist_ok=True)
    file_name = city["name"].lower().replace(" ", "_") + ".csv"
    path = os.path.join(config.RAW_DATA_DIR, file_name)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(response.text)
    return path


def extract_all():
    """Download every city in config.CITIES and return {city name: saved file path}."""
    paths = {}
    for city in config.CITIES:
        path = download_city_csv(city)
        print(f"Saved {city['name']:<13} -> {path}")
        paths[city["name"]] = path
    return paths


if __name__ == "__main__":
    extract_all()
