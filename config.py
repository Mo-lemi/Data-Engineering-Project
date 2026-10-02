"""Pipeline settings: which cities and dates to fetch, and where files go."""

# Each city needs coordinates because Open-Meteo looks weather up by
# latitude/longitude, not by name. Province is kept for the cities table.
CITIES = [
    {"name": "Johannesburg", "province": "Gauteng", "latitude": -26.2041, "longitude": 28.0473},
    {"name": "Pretoria", "province": "Gauteng", "latitude": -25.7479, "longitude": 28.2293},
    {"name": "Cape Town", "province": "Western Cape", "latitude": -33.9249, "longitude": 18.4241},
    {"name": "Durban", "province": "KwaZulu-Natal", "latitude": -29.8587, "longitude": 31.0218},
    {"name": "Bloemfontein", "province": "Free State", "latitude": -29.0852, "longitude": 26.1596},
]

START_DATE = "2020-01-01"
END_DATE = "2024-12-31"

# Daily variables requested from Open-Meteo.
DAILY_FIELDS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "precipitation_sum",
    "wind_speed_10m_max",
]

# Local time so each "day" matches a South African calendar day.
TIMEZONE = "Africa/Johannesburg"

RAW_DATA_DIR = "data/raw"
DATABASE_PATH = "weather.db"
