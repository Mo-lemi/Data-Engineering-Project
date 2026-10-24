"""Run every query in sql/queries.sql against weather.db and print the results."""

import pandas as pd

from src.load import connect

QUERIES_PATH = "sql/queries.sql"


def read_queries(path=QUERIES_PATH):
    """Split the file on ';' and return (title, sql) pairs, using each query's "-- Q" line as its title."""
    with open(path, encoding="utf-8") as f:
        statements = f.read().split(";")

    queries = []
    for statement in statements:
        title_lines = [line for line in statement.splitlines() if line.startswith("-- Q")]
        if title_lines:
            queries.append((title_lines[0][3:], statement))
    return queries


if __name__ == "__main__":
    conn = connect()
    try:
        for title, sql in read_queries():
            print(title)
            print(pd.read_sql_query(sql, conn).to_string(index=False))
            print()
    finally:
        conn.close()
