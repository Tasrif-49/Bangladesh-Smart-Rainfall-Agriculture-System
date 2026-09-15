import streamlit as st
import pandas as pd
import requests

from config.settings import (
    OPEN_METEO_ARCHIVE_URL,
    TIMEZONE
)


# ============================================================
# OPEN METEO FORECAST URL
# ============================================================

OPEN_METEO_FORECAST_URL = (
    "https://api.open-meteo.com/v1/forecast"
)


# ============================================================
# WEATHER VARIABLES
# ============================================================

DAILY_VARIABLES = [

    "rain_sum",

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

    "et0_fao_evapotranspiration"
]


# ============================================================
# COMMON API REQUEST
# ============================================================

def _fetch_open_meteo(
    url,
    lat,
    lon,
    start_date,
    end_date
):

    start_date = pd.Timestamp(
        start_date
    ).date()

    end_date = pd.Timestamp(
        end_date
    ).date()

    if start_date > end_date:

        return pd.DataFrame()

    params = {

        "latitude":
        float(lat),

        "longitude":
        float(lon),

        "daily":
        ",".join(
            DAILY_VARIABLES
        ),

        "timezone":
        TIMEZONE,

        "start_date":
        str(start_date),

        "end_date":
        str(end_date)
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    daily_data = data.get(
        "daily",
        {}
    )

    if not daily_data:

        raise ValueError(
            "Weather API returned no daily data."
        )

    if "time" not in daily_data:

        raise ValueError(
            "Weather API response has no time data."
        )

    out = pd.DataFrame(
        daily_data
    )

    out = out.rename(
        columns={
            "time":
            "Date"
        }
    )

    out["Date"] = pd.to_datetime(
        out["Date"]
    ).dt.normalize()

    return out


# ============================================================
# ARCHIVE API
# ============================================================

@st.cache_data(
    ttl=3600,
    show_spinner=False
)
def fetch_open_meteo_range(
    lat,
    lon,
    start_date,
    end_date
):

    return _fetch_open_meteo(

        url=OPEN_METEO_ARCHIVE_URL,

        lat=lat,

        lon=lon,

        start_date=start_date,

        end_date=end_date
    )


# ============================================================
# FORECAST API
# ============================================================

@st.cache_data(
    ttl=900,
    show_spinner=False
)
def fetch_open_meteo_forecast_range(
    lat,
    lon,
    start_date,
    end_date
):

    return _fetch_open_meteo(

        url=OPEN_METEO_FORECAST_URL,

        lat=lat,

        lon=lon,

        start_date=start_date,

        end_date=end_date
    )


# ============================================================
# SINGLE DATE WEATHER
# ============================================================

def fetch_target_weather(
    station,
    target_date
):

    target_date = pd.Timestamp(
        target_date
    ).normalize()

    today = pd.Timestamp(
        "today"
    ).normalize()

    lat = float(
        station["Latitude"]
    )

    lon = float(
        station["Longitude"]
    )


    # ========================================================
    # IMPORTANT:
    #
    # TODAY = ARCHIVE
    # FUTURE = FORECAST
    #
    # This preserves previous TODAY behaviour.
    # ========================================================

    if target_date <= today:

        weather_df = fetch_open_meteo_range(

            lat=lat,

            lon=lon,

            start_date=target_date,

            end_date=target_date
        )

    else:

        weather_df = fetch_open_meteo_forecast_range(

            lat=lat,

            lon=lon,

            start_date=target_date,

            end_date=target_date
        )


    if weather_df.empty:

        raise ValueError(
            "Could not fetch weather data "
            "for selected date."
        )


    # ========================================================
    # EXACT DATE
    # ========================================================

    weather_df = weather_df[
        weather_df["Date"]
        == target_date
    ].copy()


    if weather_df.empty:

        raise ValueError(
            "Selected date was not returned "
            "by weather API."
        )


    row = (
        weather_df
        .iloc[0]
        .to_dict()
    )


    return row


# ============================================================
# PREPARE LOCAL HISTORY
# ============================================================

def prepare_local_history(
    df,
    station_id,
    start_date,
    end_date
):

    local = df.copy()

    local["Date"] = pd.to_datetime(
        local["Date"]
    ).dt.normalize()

    start_date = pd.Timestamp(
        start_date
    ).normalize()

    end_date = pd.Timestamp(
        end_date
    ).normalize()


    local = local[
        (
            local["Station_ID"]
            == station_id
        )
        &
        (
            local["Date"]
            >= start_date
        )
        &
        (
            local["Date"]
            <= end_date
        )
    ].copy()


    return local


# ============================================================
# ADD STATION INFORMATION
# ============================================================

def _add_station_info(
    api_data,
    station
):

    if api_data.empty:

        return api_data


    api_data["Station_ID"] = (
        station["Station_ID"]
    )

    api_data["Latitude"] = float(
        station["Latitude"]
    )

    api_data["Longitude"] = float(
        station["Longitude"]
    )


    if "Station" in station.index:

        api_data["Station"] = (
            station["Station"]
        )


    if "District" in station.index:

        api_data["District"] = (
            station["District"]
        )


    if "Division" in station.index:

        api_data["Division"] = (
            station["Division"]
        )


    return api_data


# ============================================================
# FETCH PAST MISSING HISTORY
# ============================================================

def _fetch_missing_history(
    station,
    missing_dates
):

    if not missing_dates:

        return pd.DataFrame()


    start_date = min(
        missing_dates
    )

    end_date = max(
        missing_dates
    )


    try:

        api_data = fetch_open_meteo_range(

            lat=float(
                station["Latitude"]
            ),

            lon=float(
                station["Longitude"]
            ),

            start_date=start_date,

            end_date=end_date
        )

    except Exception:

        return pd.DataFrame()


    if api_data.empty:

        return pd.DataFrame()


    api_data = api_data[
        api_data["Date"].isin(
            missing_dates
        )
    ].copy()


    if api_data.empty:

        return pd.DataFrame()


    return _add_station_info(
        api_data,
        station
    )


# ============================================================
# FETCH RECENT / TODAY MISSING DATA
#
# IMPORTANT:
# This is only a fallback.
#
# Local CSV has priority.
# ============================================================

def _fetch_missing_recent_history(
    station,
    missing_dates
):

    if not missing_dates:

        return pd.DataFrame()


    start_date = min(
        missing_dates
    )

    end_date = max(
        missing_dates
    )


    try:

        api_data = (
            fetch_open_meteo_forecast_range(

                lat=float(
                    station["Latitude"]
                ),

                lon=float(
                    station["Longitude"]
                ),

                start_date=start_date,

                end_date=end_date
            )
        )

    except Exception:

        return pd.DataFrame()


    if api_data.empty:

        return pd.DataFrame()


    api_data = api_data[
        api_data["Date"].isin(
            missing_dates
        )
    ].copy()


    if api_data.empty:

        return pd.DataFrame()


    return _add_station_info(
        api_data,
        station
    )


# ============================================================
# BUILD ON-DEMAND HISTORY
# ============================================================

def build_on_demand_history(
    df,
    station,
    target_date,
    history_days
):

    target_date = pd.Timestamp(
        target_date
    ).normalize()

    history_days = int(
        history_days
    )


    if history_days < 30:

        history_days = 30


    # ========================================================
    # HISTORY RANGE
    # ========================================================

    start_date = (
        target_date
        - pd.Timedelta(
            days=history_days
        )
    )

    end_date = (
        target_date
        - pd.Timedelta(
            days=1
        )
    )


    station_id = (
        station["Station_ID"]
    )


    today = pd.Timestamp(
        "today"
    ).normalize()


    # ========================================================
    # LOCAL CSV
    # ========================================================

    local = prepare_local_history(

        df=df,

        station_id=station_id,

        start_date=start_date,

        end_date=end_date
    )


    # ========================================================
    # EXPECTED DATES
    # ========================================================

    expected_dates = pd.date_range(

        start=start_date,

        end=end_date,

        freq="D"
    )


    if not local.empty:

        local_dates = set(
            pd.to_datetime(
                local["Date"]
            ).dt.normalize()
        )

    else:

        local_dates = set()


    missing_dates = [

        day

        for day in expected_dates

        if day not in local_dates
    ]


    # ========================================================
    # SPLIT
    # ========================================================

    past_missing = [

        day

        for day in missing_dates

        if day < today
    ]


    recent_missing = [

        day

        for day in missing_dates

        if day >= today
    ]


    fetched_archive = pd.DataFrame()

    fetched_recent = pd.DataFrame()


    # ========================================================
    # PAST -> ARCHIVE
    # ========================================================

    if past_missing:

        fetched_archive = (
            _fetch_missing_history(

                station=station,

                missing_dates=past_missing
            )
        )


    # ========================================================
    # TODAY -> FALLBACK FORECAST
    #
    # CSV is ALWAYS given priority.
    # ========================================================

    if recent_missing:

        fetched_recent = (
            _fetch_missing_recent_history(

                station=station,

                missing_dates=recent_missing
            )
        )


    # ========================================================
    # MERGE
    # ========================================================

    history = pd.concat(

        [

            local,

            fetched_archive,

            fetched_recent

        ],

        ignore_index=True,

        sort=False
    )


    if history.empty:

        raise ValueError(
            "No historical weather data available."
        )


    # ========================================================
    # NORMALIZE DATE
    # ========================================================

    history["Date"] = pd.to_datetime(
        history["Date"]
    ).dt.normalize()


    # ========================================================
    # LOCAL CSV PRIORITY
    # ========================================================

    history = history.drop_duplicates(

        subset=[
            "Station_ID",
            "Date"
        ],

        keep="first"
    )


    # ========================================================
    # SORT
    # ========================================================

    history = history.sort_values(

        [
            "Station_ID",
            "Date"
        ]

    ).reset_index(
        drop=True
    )


    # ========================================================
    # CHECK MISSING DATES
    # ========================================================

    actual_dates = set(
        history["Date"]
    )


    still_missing = [

        day.strftime(
            "%Y-%m-%d"
        )

        for day in expected_dates

        if day not in actual_dates
    ]


    if still_missing:

        raise ValueError(

            "Historical data incomplete: "
            +
            ", ".join(
                still_missing[:10]
            )
        )


    # ========================================================
    # RAIN DATA
    # ========================================================

    if "rain_sum" not in history.columns:

        raise ValueError(
            "rain_sum column not found in history."
        )


    history["rain_sum"] = pd.to_numeric(

        history["rain_sum"],

        errors="coerce"
    )


    if history["rain_sum"].isna().any():

        missing_rain_dates = (

            history.loc[
                history["rain_sum"].isna(),
                "Date"
            ]

            .dt.strftime(
                "%Y-%m-%d"
            )

            .tolist()
        )


        raise ValueError(

            "Historical rainfall contains "
            "missing values: "
            +
            ", ".join(
                missing_rain_dates[:10]
            )
        )


    # ========================================================
    # NOTE
    # ========================================================

    local_count = len(local)

    archive_count = len(
        fetched_archive
    )

    recent_count = len(
        fetched_recent
    )


    note = (

        f"Model needs {history_days} previous days. "

        f"Used {local_count} local CSV days, "

        f"{archive_count} archive API days "

        f"and {recent_count} recent fallback API days."
    )


    # ========================================================
    # FUTURE TARGET
    # ========================================================

    if target_date > today:

        previous_day = (
            target_date
            - pd.Timedelta(
                days=1
            )
        )


        previous_row = history[

            (
                history["Date"]
                == previous_day
            )

            &

            (
                history["Station_ID"]
                == station_id
            )
        ]


        if previous_row.empty:

            raise ValueError(

                "Previous day data is missing. "
                "Future prediction cannot be created."
            )


        previous_rain = pd.to_numeric(

            previous_row.iloc[0]["rain_sum"],

            errors="coerce"
        )


        if pd.isna(previous_rain):

            raise ValueError(

                "Previous day rainfall is missing. "
                "Future prediction cannot use rain_lag_1."
            )


        # ====================================================
        # IMPORTANT NOTE
        # ====================================================

        previous_source = "API"

        if previous_day in local_dates:

            previous_source = "CSV"


        note += (

            f" Previous day rainfall "

            f"({previous_day.strftime('%d %B %Y')}) "

            f"= {float(previous_rain):.2f} mm "

            f"from {previous_source}; "

            f"this value is used for rain_lag_1 "
            f"and rolling rainfall features."
        )


        # ====================================================
        # WARNING IF TODAY WAS NOT CSV
        # ====================================================

        if previous_day == today:

            if previous_day not in local_dates:

                note += (

                    " WARNING: Today's rainfall was not "
                    "available in the CSV, so the fallback "
                    "API value was used."
                )

    return history, note