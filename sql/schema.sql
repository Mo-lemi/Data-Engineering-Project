-- SA Weather ETL database schema (SQLite).
-- IF NOT EXISTS lets the pipeline run this every time without errors.

-- One row per city. Stored once, so daily rows refer to it by id instead of repeating the details.
CREATE TABLE IF NOT EXISTS cities (
    city_id   INTEGER PRIMARY KEY,
    name      TEXT    NOT NULL UNIQUE,
    province  TEXT    NOT NULL,
    latitude  REAL    NOT NULL,
    longitude REAL    NOT NULL
);

-- One row per city per day.
CREATE TABLE IF NOT EXISTS daily_weather (
    city_id          INTEGER NOT NULL REFERENCES cities (city_id),
    date             TEXT    NOT NULL,  -- ISO format YYYY-MM-DD, so text sorting is date sorting
    temp_max_c       REAL    NOT NULL,
    temp_min_c       REAL    NOT NULL,
    precipitation_mm REAL    NOT NULL,
    wind_max_kmh     REAL    NOT NULL,
    -- The database itself refuses a second row for the same city and day.
    PRIMARY KEY (city_id, date)
);
