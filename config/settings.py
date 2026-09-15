from pathlib import Path


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# DATA DIRECTORY
# ============================================================

DATA_DIR = BASE_DIR / "data"


# ============================================================
# MODEL DIRECTORY
# ============================================================

MODEL_DIR = BASE_DIR / "models"


# ============================================================
# ASSETS DIRECTORY
# ============================================================

ASSETS_DIR = BASE_DIR / "assets"

# ============================================================

# FILE CANDIDATES

# ============================================================

MODEL_FILES = [
"rainfall_model.pkl",
"rainfall_model(4).pkl",
"rainfall_model(2).pkl"
]

CSV_FILES = [
"bangladesh_weather_stations_FINAL.csv",
"bangladesh_weather_stations_FINAL(7).csv",
"bangladesh_weather_stations_FINAL(4).csv"
]

# ============================================================

# COLORS

# ============================================================

INDIGO = "#0B1D33"

SLATE = "#1B4965"

TEAL = "#1F9E92"

AMBER = "#E8873A"

GREEN = "#2E8B57"

INK = "#0F2436"

LINE = "#D9E2EC"

# ============================================================

# OPEN METEO

# ============================================================

OPEN_METEO_ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

TIMEZONE = "Asia/Dhaka"

# ============================================================

# REQUIRED DATASET COLUMNS

# ============================================================

REQUIRED_COLUMNS = [
"Date",
"Station_ID",
"Latitude",
"Longitude",
"temperature_2m_mean",
"temperature_2m_max",
"temperature_2m_min",
"apparent_temperature_mean",
"sunshine_duration",
"daylight_duration",
"wind_speed_10m_max",
"wind_gusts_10m_max",
"wind_direction_10m_dominant",
"shortwave_radiation_sum",
"weather_code",
"et0_fao_evapotranspiration",
"rain_sum"
]
