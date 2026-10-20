"""Load step: write cleaned data into the SQLite database."""

import sqlite3

import config

SCHEMA_PATH = "sql/schema.sql"


def connect(path=config.DATABASE_PATH):
    """Open the database with foreign key checks switched on."""
    conn = sqlite3.connect(path)
    # SQLite ignores REFERENCES constraints unless this is enabled on every connection.
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def create_tables(conn):
    """Run schema.sql to create any tables that don't exist yet."""
    with open(SCHEMA_PATH, encoding="utf-8") as f:
        conn.executescript(f.read())


def load_cities(conn, cities=config.CITIES):
    """Insert each city, or update its details if it is already there."""
    # An upsert keeps each city's existing city_id, so daily_weather rows stay linked to it.
    sql = """
        INSERT INTO cities (name, province, latitude, longitude)
        VALUES (:name, :province, :latitude, :longitude)
        ON CONFLICT (name) DO UPDATE SET
            province  = excluded.province,
            latitude  = excluded.latitude,
            longitude = excluded.longitude
    """
    # "with conn" commits if everything succeeds, and rolls back if anything fails.
    with conn:
        conn.executemany(sql, cities)


def load_daily_weather(conn, df):
    """Insert cleaned daily rows, replacing any row already stored for the same city and day."""
    # The DataFrame has city names; the table needs city ids, so look them up from cities.
    city_ids = dict(conn.execute("SELECT name, city_id FROM cities"))
    df = df.copy()
    df["city_id"] = df["city"].map(city_ids)
    if df["city_id"].isna().any():
        raise ValueError("Some rows belong to a city that is not in the cities table")
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")

    # Same upsert idea as load_cities: re-running replaces rows instead of duplicating them.
    sql = """
        INSERT INTO daily_weather
            (city_id, date, temp_max_c, temp_min_c, precipitation_mm, wind_max_kmh)
        VALUES
            (:city_id, :date, :temp_max_c, :temp_min_c, :precipitation_mm, :wind_max_kmh)
        ON CONFLICT (city_id, date) DO UPDATE SET
            temp_max_c       = excluded.temp_max_c,
            temp_min_c       = excluded.temp_min_c,
            precipitation_mm = excluded.precipitation_mm,
            wind_max_kmh     = excluded.wind_max_kmh
    """
    with conn:
        conn.executemany(sql, df.to_dict("records"))


if __name__ == "__main__":
    conn = connect()
    create_tables(conn)
    load_cities(conn)
    for row in conn.execute("SELECT * FROM cities ORDER BY city_id"):
        print(row)
    conn.close()
