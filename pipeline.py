"""Run the whole ETL pipeline: python pipeline.py"""

import pandas as pd

from src.extract import extract_all
from src.load import connect, create_tables, load_cities, load_daily_weather
from src.transform import clean_weather, read_city_csv


def run():
    print("1/3 Extract")
    paths = extract_all()

    print("2/3 Transform")
    frames = []
    for city_name, path in paths.items():
        raw = read_city_csv(path, city_name)
        clean = clean_weather(raw)
        print(f"  {city_name:<13} {len(raw)} rows read, {len(raw) - len(clean)} removed")
        frames.append(clean)
    weather = pd.concat(frames, ignore_index=True)

    print("3/3 Load")
    conn = connect()
    try:
        create_tables(conn)
        load_cities(conn)
        load_daily_weather(conn, weather)
        total = conn.execute("SELECT COUNT(*) FROM daily_weather").fetchone()[0]
        print(f"  daily_weather now holds {total} rows")
    finally:
        # Close the database even if a step above fails.
        conn.close()

    print("Done")


if __name__ == "__main__":
    run()
