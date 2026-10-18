"""Tests for the cleaning rules in src/transform.py."""

import pandas as pd

from src.transform import clean_weather


def make_rows(rows):
    """Build a small DataFrame shaped like read_city_csv's output."""
    columns = ["city", "date", "temp_max_c", "temp_min_c", "precipitation_mm", "wind_max_kmh"]
    df = pd.DataFrame(rows, columns=columns)
    df["date"] = pd.to_datetime(df["date"])
    return df


def test_keeps_valid_rows():
    df = make_rows([
        ("Durban", "2024-01-01", 30.0, 22.0, 1.5, 20.0),
        ("Durban", "2024-01-02", 29.0, 21.0, 0.0, 18.0),
    ])
    assert len(clean_weather(df)) == 2


def test_removes_duplicate_dates():
    df = make_rows([
        ("Durban", "2024-01-01", 30.0, 22.0, 1.5, 20.0),
        ("Durban", "2024-01-01", 30.0, 22.0, 1.5, 20.0),
    ])
    assert len(clean_weather(df)) == 1


def test_same_date_in_different_cities_is_not_a_duplicate():
    df = make_rows([
        ("Durban", "2024-01-01", 30.0, 22.0, 1.5, 20.0),
        ("Cape Town", "2024-01-01", 25.0, 15.0, 0.0, 30.0),
    ])
    assert len(clean_weather(df)) == 2


def test_removes_rows_with_missing_values():
    df = make_rows([
        ("Durban", "2024-01-01", 30.0, 22.0, None, 20.0),
        ("Durban", "2024-01-02", 29.0, 21.0, 0.0, 18.0),
    ])
    cleaned = clean_weather(df)
    assert len(cleaned) == 1
    assert cleaned["date"][0] == pd.Timestamp("2024-01-02")


def test_removes_impossible_values():
    df = make_rows([
        ("Durban", "2024-01-01", 20.0, 25.0, 0.0, 10.0),   # min above max
        ("Durban", "2024-01-02", 29.0, 21.0, -1.0, 18.0),  # negative rain
        ("Durban", "2024-01-03", 29.0, 21.0, 0.0, -5.0),   # negative wind
        ("Durban", "2024-01-04", 29.0, 21.0, 0.0, 18.0),   # valid
    ])
    cleaned = clean_weather(df)
    assert len(cleaned) == 1
    assert cleaned["date"][0] == pd.Timestamp("2024-01-04")
