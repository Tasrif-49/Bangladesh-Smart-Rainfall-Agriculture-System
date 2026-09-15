import streamlit as st
import pandas as pd
import pickle

from config.settings import (
    MODEL_DIR,
    DATA_DIR,
    MODEL_FILES,
    CSV_FILES,
    REQUIRED_COLUMNS
)


# ============================================================
# LOAD MODEL
# ============================================================

@st.cache_resource
def load_model():

    for filename in MODEL_FILES:

        file_path = MODEL_DIR / filename

        if file_path.exists():

            with open(file_path, "rb") as f:

                package = pickle.load(f)

            return package, filename

    raise FileNotFoundError(
        f"""
        Model file not found.

        Put your PKL file inside:

        {MODEL_DIR}
        """
    )


# ============================================================
# LOAD DATASET
# ============================================================

@st.cache_data
def load_dataset():

    for filename in CSV_FILES:

        file_path = DATA_DIR / filename

        if file_path.exists():

            df = pd.read_csv(file_path)

            return df, filename

    raise FileNotFoundError(
        f"""
        CSV file not found.

        Put your CSV file inside:

        {DATA_DIR}
        """
    )


# ============================================================
# VALIDATE DATASET
# ============================================================

def validate_dataset(df):

    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            f"Missing required columns: {missing}"
        )

    return True


# ============================================================
# PREPARE DATASET
# ============================================================

def prepare_dataset(df):

    df = df.copy()

    # ========================================================
    # DATE CONVERSION
    # ========================================================

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    # Remove invalid dates

    df = df.dropna(
        subset=["Date"]
    ).copy()

    # Remove time component

    df["Date"] = (
        df["Date"]
        .dt.normalize()
    )

    # ========================================================
    # SORT
    # ========================================================

    df = (
        df
        .sort_values(
            [
                "Station_ID",
                "Date"
            ]
        )
        .reset_index(
            drop=True
        )
    )

    # ========================================================
    # OPTIONAL COLUMNS
    # ========================================================

    for column in [
        "Station",
        "District",
        "Division"
    ]:

        if column not in df.columns:

            df[column] = (
                df["Station_ID"]
                .astype(str)
            )

    return df


# ============================================================
# GET STATION TABLE
# ============================================================

def get_station_table(df):

    meta = (
        df
        .groupby(
            "Station_ID",
            as_index=False
        )
        .agg(
            Station=(
                "Station",
                "first"
            ),

            District=(
                "District",
                "first"
            ),

            Division=(
                "Division",
                "first"
            ),

            Latitude=(
                "Latitude",
                "median"
            ),

            Longitude=(
                "Longitude",
                "median"
            )
        )
    )

    return meta


# ============================================================
# GET MODEL HISTORY DAYS
# ============================================================

def get_model_history_days(
    feature_columns
):

    import re

    rain_lags = []
    roll_windows = []
    weather_lags = []

    for col in feature_columns:

        # ====================================================
        # RAIN LAG
        # ====================================================

        m = re.fullmatch(
            r"rain_lag_(\d+)",
            col
        )

        if m:

            rain_lags.append(
                int(m.group(1))
            )

            continue

        # ====================================================
        # ROLLING
        # ====================================================

        m = re.fullmatch(
            r"rain_roll_(?:mean|sum|std)_(\d+)",
            col
        )

        if m:

            roll_windows.append(
                int(m.group(1))
            )

            continue

        # ====================================================
        # WEATHER LAG
        # ====================================================

        m = re.fullmatch(
            r"(.+)_lag_(\d+)",
            col
        )

        if (
            m
            and not col.startswith("rain_")
        ):

            weather_lags.append(
                int(m.group(2))
            )

    return max(
        rain_lags
        +
        roll_windows
        +
        weather_lags
        +
        [1]
    )