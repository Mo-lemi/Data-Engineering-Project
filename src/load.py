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


if __name__ == "__main__":
    conn = connect()
    create_tables(conn)
    load_cities(conn)
    for row in conn.execute("SELECT * FROM cities ORDER BY city_id"):
        print(row)
    conn.close()
