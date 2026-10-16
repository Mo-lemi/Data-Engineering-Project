"""Transform step: turn raw Open-Meteo CSVs into clean, consistently named tables."""

import pandas as pd

# Open-Meteo puts 2 lines of location metadata and a blank line above the real header.
METADATA_ROWS = 3

# Raw column names include units, which are awkward in SQL. Keep the unit in the new name instead.
COLUMN_NAMES = {
    "time": "date",
    "temperature_2m_max (°C)": "temp_max_c",
    "temperature_2m_min (°C)": "temp_min_c",
    "precipitation_sum (mm)": "precipitation_mm",
    "wind_speed_10m_max (km/h)": "wind_max_kmh",
}


def read_city_csv(path, city_name):
    """Read one raw CSV into a DataFrame with clean column names and a city column."""
    df = pd.read_csv(path, skiprows=METADATA_ROWS, encoding="utf-8")
    df = df.rename(columns=COLUMN_NAMES)
    # An explicit format makes a malformed date fail loudly instead of being guessed.
    df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")
    df.insert(0, "city", city_name)
    return df


if __name__ == "__main__":
    df = read_city_csv("data/raw/johannesburg.csv", "Johannesburg")
    print(df.head())
    print()
    print(df.dtypes)
    print()
    print(len(df), "rows")
