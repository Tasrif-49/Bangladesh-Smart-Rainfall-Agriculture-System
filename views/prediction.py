import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from datetime import date

from services.data_loader import get_station_table

from services.weather_api import (
    build_on_demand_history,
    fetch_target_weather
)


# ============================================================
# WEATHER CONDITION
# ============================================================

def condition(code, pred=None):

    if pred is not None:

        if pred < 1:
            return (
                "☀️ Sunny",
                "Mostly dry conditions expected."
            )

        elif pred < 10:
            return (
                "🌤️ Light Rain",
                "Light rainfall is possible."
            )

        elif pred < 25:
            return (
                "🌧️ Moderate Rain",
                "Noticeable rainfall is expected."
            )

        elif pred < 50:
            return (
                "⛈️ Heavy Rain",
                "Heavy rainfall expected."
            )

        else:
            return (
                "🚨 Very Heavy Rain",
                "Very heavy rainfall expected."
            )

    if code in [0, 1]:

        return (
            "☀️ Sunny",
            "Clear weather."
        )

    elif code in [2, 3, 45, 48]:

        return (
            "☁️ Cloudy",
            "Cloudy conditions."
        )

    else:

        return (
            "🌧️ Rainy",
            "Rainy conditions."
        )


# ============================================================
# RAIN PROBABILITY
# ============================================================

def estimate_rain_probability(pred):

    """
    Estimate rainfall likelihood from predicted rainfall amount.

    IMPORTANT:
    This is an estimated UI score based on predicted rainfall.
    It is NOT a calibrated statistical probability from the
    regression model.
    """

    pred = max(float(pred), 0.0)

    if pred <= 0:

        probability = 5.0

    else:

        probability = 100 * (
            1 - np.exp(-pred / 18)
        )

    probability = min(
        max(probability, 0),
        100
    )

    return probability


# ============================================================
# SAFE NUMBER
# ============================================================

def safe_float(value, default=0.0):

    try:

        if pd.isna(value):

            return float(default)

        return float(value)

    except Exception:

        return float(default)


# ============================================================
# CREATE PREDICTION FEATURES
# ============================================================

def create_prediction_features(
    historical_df,
    station_id,
    target_date,
    weather_values,
    feature_columns,
    train_medians
):

    data = historical_df.copy()

    data["Date"] = pd.to_datetime(
        data["Date"],
        errors="coerce"
    ).dt.normalize()

    target_date = pd.Timestamp(
        target_date
    ).normalize()

    data = data.sort_values(
        ["Station_ID", "Date"]
    ).reset_index(drop=True)

    data = data[
        ~(
            (data["Station_ID"] == station_id)
            &
            (data["Date"] == target_date)
        )
    ].copy()

    # ========================================================
    # TARGET ROW
    # ========================================================

    target_row = {

        "Date": target_date,

        "Station_ID": station_id,

        "Latitude": safe_float(
            weather_values.get("Latitude")
        ),

        "Longitude": safe_float(
            weather_values.get("Longitude")
        ),

        "temperature_2m_mean": safe_float(
            weather_values.get(
                "temperature_2m_mean"
            )
        ),

        "temperature_2m_max": safe_float(
            weather_values.get(
                "temperature_2m_max"
            )
        ),

        "temperature_2m_min": safe_float(
            weather_values.get(
                "temperature_2m_min"
            )
        ),

        "apparent_temperature_mean": safe_float(
            weather_values.get(
                "apparent_temperature_mean"
            )
        ),

        "sunshine_duration": safe_float(
            weather_values.get(
                "sunshine_duration"
            )
        ),

        "daylight_duration": safe_float(
            weather_values.get(
                "daylight_duration"
            )
        ),

        "wind_speed_10m_max": safe_float(
            weather_values.get(
                "wind_speed_10m_max"
            )
        ),

        "wind_gusts_10m_max": safe_float(
            weather_values.get(
                "wind_gusts_10m_max"
            )
        ),

        "wind_direction_10m_dominant": safe_float(
            weather_values.get(
                "wind_direction_10m_dominant"
            )
        ),

        "shortwave_radiation_sum": safe_float(
            weather_values.get(
                "shortwave_radiation_sum"
            )
        ),

        "weather_code": safe_float(
            weather_values.get(
                "weather_code"
            )
        ),

        "et0_fao_evapotranspiration": safe_float(
            weather_values.get(
                "et0_fao_evapotranspiration"
            )
        ),

        "rain_sum": np.nan
    }

    target_df = pd.DataFrame(
        [target_row]
    )

    data = pd.concat(
        [
            data,
            target_df
        ],
        ignore_index=True,
        sort=False
    )

    data = data.sort_values(
        ["Station_ID", "Date"]
    ).reset_index(drop=True)

    # ========================================================
    # CALENDAR FEATURES
    # ========================================================

    data["year"] = data["Date"].dt.year

    data["month"] = data["Date"].dt.month

    data["day"] = data["Date"].dt.day

    data["dayofyear"] = (
        data["Date"].dt.dayofyear
    )

    data["dayofweek"] = (
        data["Date"].dt.dayofweek
    )

    data["weekofyear"] = (
        data["Date"]
        .dt.isocalendar()
        .week
        .astype(int)
    )

    # ========================================================
    # CYCLIC FEATURES
    # ========================================================

    data["month_sin"] = (
        np.sin(
            2 * np.pi * data["month"] / 12
        )
    )

    data["month_cos"] = (
        np.cos(
            2 * np.pi * data["month"] / 12
        )
    )

    data["dayofyear_sin"] = (
        np.sin(
            2 * np.pi
            * data["dayofyear"]
            / 365.25
        )
    )

    data["dayofyear_cos"] = (
        np.cos(
            2 * np.pi
            * data["dayofyear"]
            / 365.25
        )
    )

    data["dayofweek_sin"] = (
        np.sin(
            2 * np.pi
            * data["dayofweek"]
            / 7
        )
    )

    data["dayofweek_cos"] = (
        np.cos(
            2 * np.pi
            * data["dayofweek"]
            / 7
        )
    )

    # ========================================================
    # RAIN LAGS
    # ========================================================

    RAIN_LAGS = [
        1,
        2,
        3,
        5,
        7,
        14,
        21,
        30
    ]

    for lag in RAIN_LAGS:

        data[
            f"rain_lag_{lag}"
        ] = (
            data
            .groupby("Station_ID")["rain_sum"]
            .shift(lag)
        )

    # ========================================================
    # RAIN OCCURRENCE
    # ========================================================

    rain_occurrence = (
        data["rain_sum"] > 0
    ).astype(int)

    for lag in [1, 2, 3, 7]:

        data[
            f"rain_occurrence_lag_{lag}"
        ] = (
            rain_occurrence
            .groupby(data["Station_ID"])
            .shift(lag)
        )

    # ========================================================
    # ROLLING FEATURES
    # ========================================================

    shifted_rain = (
        data
        .groupby("Station_ID")["rain_sum"]
        .shift(1)
    )

    for window in [3, 7, 14, 30]:

        data[
            f"rain_roll_mean_{window}"
        ] = (
            shifted_rain
            .groupby(data["Station_ID"])
            .transform(
                lambda x:
                x.rolling(
                    window=window,
                    min_periods=1
                ).mean()
            )
        )

        data[
            f"rain_roll_sum_{window}"
        ] = (
            shifted_rain
            .groupby(data["Station_ID"])
            .transform(
                lambda x:
                x.rolling(
                    window=window,
                    min_periods=1
                ).sum()
            )
        )

        data[
            f"rain_roll_std_{window}"
        ] = (
            shifted_rain
            .groupby(data["Station_ID"])
            .transform(
                lambda x:
                x.rolling(
                    window=window,
                    min_periods=2
                ).std()
            )
        )

    # ========================================================
    # WEATHER LAGS
    # ========================================================

    same_day_weather = [

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

    for feature in same_day_weather:

        for lag in [1, 2, 3, 7]:

            data[
                f"{feature}_lag_{lag}"
            ] = (
                data
                .groupby("Station_ID")[feature]
                .shift(lag)
            )

    # ========================================================
    # STATION DUMMIES
    # ========================================================

    station_dummies = pd.get_dummies(
        data["Station_ID"],
        prefix="station",
        dtype=int
    )

    data = pd.concat(
        [
            data,
            station_dummies
        ],
        axis=1
    )

    # ========================================================
    # GET TARGET ROW
    # ========================================================

    prediction_row = data[
        (data["Station_ID"] == station_id)
        &
        (data["Date"] == target_date)
    ].copy()

    if len(prediction_row) != 1:

        raise ValueError(
            "Could not create prediction row."
        )

    # ========================================================
    # MODEL FEATURES
    # ========================================================

    X_prediction = (
        prediction_row
        .reindex(columns=feature_columns)
    )

    # ========================================================
    # NUMERIC CONVERSION
    # ========================================================

    for col in X_prediction.columns:

        X_prediction[col] = pd.to_numeric(
            X_prediction[col],
            errors="coerce"
        )

    X_prediction = X_prediction.replace(
        [np.inf, -np.inf],
        np.nan
    )

    # ========================================================
    # STATION HISTORY
    # ========================================================

    station_history = data[
        (data["Station_ID"] == station_id)
        &
        (data["Date"] < target_date)
    ].copy()

    station_history = (
        station_history
        .reindex(columns=feature_columns)
    )

    for col in station_history.columns:

        station_history[col] = pd.to_numeric(
            station_history[col],
            errors="coerce"
        )

    station_medians = (
        station_history
        .median(numeric_only=True)
    )

    # ========================================================
    # FILL MISSING
    # ========================================================

    X_prediction = (
        X_prediction
        .fillna(station_medians)
    )

    X_prediction = (
        X_prediction
        .fillna(train_medians)
    )

    X_prediction = (
        X_prediction
        .fillna(0)
    )

    # ========================================================
    # FINAL COLUMN ORDER
    # ========================================================

    X_prediction = (
        X_prediction
        .reindex(
            columns=feature_columns,
            fill_value=0
        )
    )

    return X_prediction


# ============================================================
# LOAD WEATHER VALUES
# ============================================================

def load_weather_values(
    station,
    target
):

    try:

        weather = fetch_target_weather(
            station=station,
            target_date=target
        )

        weather["Latitude"] = float(
            station["Latitude"]
        )

        weather["Longitude"] = float(
            station["Longitude"]
        )

        return weather, None

    except Exception as e:

        return None, str(e)


# ============================================================
# PREDICTION PAGE
# ============================================================

def show_prediction(
    df,
    model,
    feature_columns,
    train_medians,
    history_days
):

    # ========================================================
    # PAGE TITLE
    # ========================================================

    st.title(
        "🔮 Rainfall Prediction"
    )

    st.caption(
        "Use weather data according to station and date "
        "to predict rainfall using the CatBoost model. "
        "For future prediction, previous rainfall data "
        "is used for lag and rolling features."
    )

    # ========================================================
    # STATION DATA
    # ========================================================

    meta = get_station_table(df).copy()

    meta["label"] = meta.apply(
        lambda x:
        f"{x['Station']}, "
        f"{x['District']} "
        f"({x['Division']})",
        axis=1
    )

    labels = sorted(
        meta["label"].tolist()
    )

    # ========================================================
    # STATION SELECT
    # ========================================================

    selected_label = st.selectbox(
        "📍 Select Station",
        labels,
        key="prediction_station"
    )

    station = meta.loc[
        meta["label"] == selected_label
    ].iloc[0]

    # ========================================================
    # DATE SELECT
    # ========================================================

    today = date.today()

    # ========================================================
    # STREAMLIT CALENDAR (DATE CHANGE FIX)
    # ========================================================

    if "prediction_date" not in st.session_state:
        st.session_state.prediction_date = today

    selected_date = st.date_input(
        "📅 Prediction Date",
        value=st.session_state.prediction_date,
        key="calendar_date",
        format="YYYY/MM/DD",
        on_change=lambda: st.session_state.update(
            prediction_date=st.session_state.calendar_date
        )
    )

    # Always update target after calendar change
    st.session_state.prediction_date = selected_date

    target = pd.Timestamp(
        selected_date
    ).normalize()

    # ========================================================
    # STATUS
    # ========================================================

    is_future = selected_date > today

    is_today = selected_date == today

    is_past = selected_date < today

    if is_future:

        st.info(
            "🔮 Future Forecast Mode: "
            "Forecast weather data will be used "
            "for rainfall prediction. Previous rainfall "
            "data will be used for lag and rolling features."
        )

    elif is_today:

        st.info(
            "📅 Today Mode: "
            "Today's weather data will use the "
            "historical/archive weather source."
        )

    elif is_past:

        st.info(
            "📚 Historical Mode: "
            "Historical/archive weather data will be used "
            "for the selected date."
        )

    # ========================================================
    # SESSION KEY
    # ========================================================

    weather_key = (
        f"{station['Station_ID']}_"
        f"{target.strftime('%Y%m%d')}"
    )

    # Clear cached weather/result whenever station or date changes
    if (
        st.session_state.get("last_calendar_key")
        != weather_key
    ):
        st.session_state.last_calendar_key = weather_key

        if "weather_data_key" in st.session_state:
            del st.session_state.weather_data_key

        if "weather_values" in st.session_state:
            del st.session_state.weather_values

        if "rain_prediction" in st.session_state:
            del st.session_state.rain_prediction

    # ========================================================
    # CLEAR OLD RESULT
    # ========================================================

    if "last_prediction_key" in st.session_state:

        if (
            st.session_state.last_prediction_key
            != weather_key
        ):

            if "rain_prediction" in st.session_state:

                del st.session_state[
                    "rain_prediction"
                ]

    # ========================================================
    # FETCH WEATHER BUTTON
    # ========================================================

    col1, col2 = st.columns([1, 3])

    with col1:

        refresh_weather = st.button(
            "🔄 Load Weather Data",
            width="stretch",
            key="refresh_prediction_weather"
        )

    # ========================================================
    # AUTO FETCH
    # ========================================================

    if (
        refresh_weather
        or
        "weather_data_key" not in st.session_state
        or
        st.session_state.weather_data_key
        != weather_key
    ):

        with st.spinner(
            "Loading station weather data..."
        ):

            weather_data, error = (
                load_weather_values(
                    station=station,
                    target=target
                )
            )

            if error:

                st.warning(
                    "⚠️ Real weather data could not be loaded. "
                    "CSV median values are being used."
                )

                st.session_state.weather_values = None

                st.session_state.weather_error = error

            else:

                st.session_state.weather_values = (
                    weather_data
                )

                st.session_state.weather_error = None

            st.session_state.weather_data_key = (
                weather_key
            )

    # ========================================================
    # BASE CSV MEDIAN
    # ========================================================

    station_df = df[
        df["Station_ID"] == station["Station_ID"]
    ].copy()

    base = (
        station_df
        .median(numeric_only=True)
        .to_dict()
    )

    # ========================================================
    # WEATHER DATA
    # ========================================================

    api_values = st.session_state.get(
        "weather_values",
        None
    )

    if api_values is None:

        values_source = base

        st.info(
            "ℹ️ Default CSV values are being displayed. "
            "You can edit them if needed."
        )

    else:

        values_source = api_values

        if is_future:

            st.success(
                f"🔮 Forecast Weather Loaded: "
                f"{target.strftime('%Y-%m-%d')}"
            )

        elif is_today:

            st.success(
                f"✅ Today's Weather Data Loaded: "
                f"{target.strftime('%Y-%m-%d')}"
            )

        else:

            st.success(
                f"📚 Historical Weather Data Loaded: "
                f"{target.strftime('%Y-%m-%d')}"
            )

    # ========================================================
    # WEATHER FORM
    # ========================================================

    with st.form(
        "prediction_weather_form"
    ):

        st.subheader(
            "🌦️ Weather Information"
        )

        st.caption(
            "Weather values have been loaded automatically. "
            "You can edit any value if needed."
        )

        # ====================================================
        # ROW 1
        # ====================================================

        c1, c2, c3, c4 = st.columns(4)

        mean_temp = c1.number_input(
            "Mean Temperature °C",
            value=safe_float(
                values_source.get(
                    "temperature_2m_mean"
                ),
                25
            )
        )

        max_temp = c2.number_input(
            "Max Temperature °C",
            value=safe_float(
                values_source.get(
                    "temperature_2m_max"
                ),
                30
            )
        )

        min_temp = c3.number_input(
            "Min Temperature °C",
            value=safe_float(
                values_source.get(
                    "temperature_2m_min"
                ),
                20
            )
        )

        apparent_temp = c4.number_input(
            "Apparent Temperature °C",
            value=safe_float(
                values_source.get(
                    "apparent_temperature_mean"
                ),
                25
            )
        )

        # ====================================================
        # ROW 2
        # ====================================================

        c1, c2, c3, c4 = st.columns(4)

        sunshine = c1.number_input(
            "Sunshine Duration",
            value=safe_float(
                values_source.get(
                    "sunshine_duration"
                )
            )
        )

        daylight = c2.number_input(
            "Daylight Duration",
            value=safe_float(
                values_source.get(
                    "daylight_duration"
                )
            )
        )

        wind_speed = c3.number_input(
            "Wind Speed",
            value=safe_float(
                values_source.get(
                    "wind_speed_10m_max"
                )
            )
        )

        wind_gusts = c4.number_input(
            "Wind Gusts",
            value=safe_float(
                values_source.get(
                    "wind_gusts_10m_max"
                )
            )
        )

        # ====================================================
        # ROW 3
        # ====================================================

        c1, c2, c3, c4 = st.columns(4)

        wind_direction = c1.number_input(
            "Wind Direction",
            value=safe_float(
                values_source.get(
                    "wind_direction_10m_dominant"
                )
            )
        )

        radiation = c2.number_input(
            "Shortwave Radiation",
            value=safe_float(
                values_source.get(
                    "shortwave_radiation_sum"
                )
            )
        )

        weather_code = c3.number_input(
            "Weather Code",
            value=int(
                safe_float(
                    values_source.get(
                        "weather_code"
                    )
                )
            ),
            step=1
        )

        et0 = c4.number_input(
            "ET0",
            value=safe_float(
                values_source.get(
                    "et0_fao_evapotranspiration"
                )
            )
        )

        submitted = st.form_submit_button(
            "🌧️ Predict Rainfall",
            type="primary",
            width="stretch"
        )

    # ========================================================
    # PREDICT
    # ========================================================

    if submitted:

        try:

            # =================================================
            # WEATHER VALUES
            # =================================================

            values = {

                "Latitude":
                float(
                    station["Latitude"]
                ),

                "Longitude":
                float(
                    station["Longitude"]
                ),

                "temperature_2m_mean":
                mean_temp,

                "temperature_2m_max":
                max_temp,

                "temperature_2m_min":
                min_temp,

                "apparent_temperature_mean":
                apparent_temp,

                "sunshine_duration":
                sunshine,

                "daylight_duration":
                daylight,

                "wind_speed_10m_max":
                wind_speed,

                "wind_gusts_10m_max":
                wind_gusts,

                "wind_direction_10m_dominant":
                wind_direction,

                "shortwave_radiation_sum":
                radiation,

                "weather_code":
                int(weather_code),

                "et0_fao_evapotranspiration":
                et0
            }

            # =================================================
            # HISTORY
            # =================================================

            with st.spinner(
                "Preparing historical rainfall data..."
            ):

                pred_hist, bridge_note = (
                    build_on_demand_history(
                        df=df,
                        station=station,
                        target_date=target,
                        history_days=history_days
                    )
                )

            # =================================================
            # FUTURE CHECK
            # =================================================

            if is_future:

                target_previous_day = (
                    target - pd.Timedelta(days=1)
                )

                previous_day = pred_hist[
                    (
                        pd.to_datetime(
                            pred_hist["Date"]
                        ).dt.normalize()
                        == target_previous_day
                    )
                    &
                    (
                        pred_hist["Station_ID"]
                        == station["Station_ID"]
                    )
                ]

                if previous_day.empty:

                    raise ValueError(
                        "Previous day's rainfall data "
                        "could not be prepared for "
                        "future prediction."
                    )

                previous_rain = pd.to_numeric(
                    previous_day.iloc[0][
                        "rain_sum"
                    ],
                    errors="coerce"
                )

                if pd.isna(previous_rain):

                    raise ValueError(
                        "Previous day's rainfall value "
                        "is missing."
                    )

            # =================================================
            # FEATURES
            # =================================================

            with st.spinner(
                "Creating rolling and lag features..."
            ):

                X = create_prediction_features(
                    historical_df=pred_hist,
                    station_id=station["Station_ID"],
                    target_date=target,
                    weather_values=values,
                    feature_columns=feature_columns,
                    train_medians=train_medians
                )

            # =================================================
            # VALIDATION
            # =================================================

            if X.empty:

                raise ValueError(
                    "Prediction features are empty."
                )

            if len(X.columns) != len(feature_columns):

                raise ValueError(
                    "Feature column count does not "
                    "match model."
                )

            nan_count = int(
                X.isna().sum().sum()
            )

            if nan_count > 0:

                raise ValueError(
                    f"Prediction features contain "
                    f"{nan_count} NaN values."
                )

            # =================================================
            # MODEL PREDICTION
            # =================================================

            with st.spinner(
                "CatBoost model is predicting..."
            ):

                prediction_array = np.asarray(
                    model.predict(X)
                ).reshape(-1)

            if len(prediction_array) == 0:

                raise ValueError(
                    "Model returned no prediction."
                )

            pred = max(
                float(prediction_array[0]),
                0.0
            )

            # =================================================
            # CONDITION
            # =================================================

            weather_name, message = condition(
                code=int(weather_code),
                pred=pred
            )

            # =================================================
            # RAIN PROBABILITY
            # =================================================

            rain_probability = (
                estimate_rain_probability(pred)
            )

            # =================================================
            # SAVE RESULT
            # =================================================

            st.session_state.rain_prediction = {

                "prediction":
                pred,

                "rain_probability":
                rain_probability,

                "station":
                station,

                "date":
                target,

                "weather_values":
                values,

                "condition":
                weather_name,

                "message":
                message,

                "et0":
                float(et0),

                "history_note":
                bridge_note,

                "is_future":
                is_future
            }

            st.session_state.last_prediction_key = (
                weather_key
            )

        except Exception as e:

            st.error(
                "❌ Prediction Failed"
            )

            st.exception(e)

    # ========================================================
    # RESULT
    # ========================================================

    if "rain_prediction" in st.session_state:

        result = (
            st.session_state.rain_prediction
        )

        same_station = (
            result["station"]["Station_ID"]
            == station["Station_ID"]
        )

        same_date = (
            pd.Timestamp(
                result["date"]
            ).normalize()
            == target
        )

        if same_station and same_date:

            pred = result["prediction"]

            st.divider()

            # =================================================
            # RAIN PROBABILITY (ABOVE RESULT METRICS)
            # =================================================

            probability = float(
                result.get(
                    "rain_probability",
                    estimate_rain_probability(
                        pred
                    )
                )
            )

            st.markdown(
                "### 🌧️ Rainfall Probability"
            )

            # =================================================
            # SPEEDOMETER STYLE RAIN PROBABILITY GAUGE
            # =================================================

            theta = np.linspace(0, 180, 120)
            # =================================================
            # PERFECT DONUT STYLE DASHBOARD SPEEDOMETER
            # =================================================

            import math

            fig = go.Figure()

            # Donut style semicircle using scatter filled shapes
            center_x = 0
            center_y = 0

            outer_r = 1.0
            inner_r = 0.78

            segments = [
                (0, 25, "#22C55E"),
                (25, 50, "#FACC15"),
                (50, 75, "#FB923C"),
                (75, 100, "#EF4444")
            ]

            for low, high, color in segments:

                a1 = math.pi - math.pi * high / 100
                a2 = math.pi - math.pi * low / 100

                angles = np.linspace(a1, a2, 120)

                x_outer = outer_r * np.cos(angles)
                y_outer = outer_r * np.sin(angles)

                x_inner = inner_r * np.cos(angles[::-1])
                y_inner = inner_r * np.sin(angles[::-1])

                x = np.concatenate([x_outer, x_inner])
                y = np.concatenate([y_outer, y_inner])

                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=y,
                        fill="toself",
                        mode="lines",
                        line=dict(
                            width=0
                        ),
                        fillcolor=color,
                        hoverinfo="skip",
                        showlegend=False
                    )
                )

            # Inner white face
            face_angles = np.linspace(math.pi, 0, 200)

            fig.add_trace(
                go.Scatter(
                    x=inner_r*np.cos(face_angles),
                    y=inner_r*np.sin(face_angles),
                    fill="toself",
                    mode="lines",
                    line=dict(width=0),
                    fillcolor="#FFFFFF",
                    hoverinfo="skip",
                    showlegend=False
                )
            )

            # Needle
            needle_angle = math.pi - math.pi * probability / 100

            fig.add_trace(
                go.Scatter(
                    x=[
                        0,
                        0.68*math.cos(needle_angle)
                    ],
                    y=[
                        0,
                        0.68*math.sin(needle_angle)
                    ],
                    mode="lines",
                    line=dict(
                        color="#F97316",
                        width=6
                    ),
                    hoverinfo="skip",
                    showlegend=False
                )
            )

            # Center knob
            fig.add_trace(
                go.Scatter(
                    x=[0],
                    y=[0],
                    mode="markers",
                    marker=dict(
                        size=18,
                        color="#F97316",
                        line=dict(
                            color="white",
                            width=3
                        )
                    ),
                    hoverinfo="skip",
                    showlegend=False
                )
            )

            fig.add_annotation(
                x=0,
                y=0.25,
                text=f"<b>{probability:.1f}%</b>",
                showarrow=False,
                font=dict(
                    size=38,
                    color="#0F172A"
                )
            )

            fig.add_annotation(
                x=0,
                y=-0.05,
                text="RAIN PROBABILITY",
                showarrow=False,
                font=dict(
                    size=12,
                    color="#64748B"
                )
            )

            fig.update_layout(
                height=330,
                autosize=True,
                margin=dict(
                    l=20,
                    r=20,
                    t=10,
                    b=10
                ),
                dragmode=False,
                hovermode=False,
                xaxis=dict(
                    visible=False,
                    fixedrange=True,
                    range=[-1.15,1.15],
                    scaleanchor="y",
                    scaleratio=1
                ),
                yaxis=dict(
                    visible=False,
                    fixedrange=True,
                    range=[-0.2,1.1]
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)"
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={
                    "displayModeBar": False,
                    "scrollZoom": False,
                    "doubleClick": False,
                    "staticPlot": True,
                    "responsive": True
                }
            )

            st.caption(
                "Probability is estimated from the predicted rainfall amount."
            )

            # =================================================
            # PREDICTION RESULT TITLE (WITH METRICS)
            # =================================================

            if result.get(
                "is_future",
                False
            ):

                st.subheader(
                    "🔮 Future Prediction Result"
                )

            else:

                st.subheader(
                    "🌧️ Prediction Result"
                )

            # =================================================
            # MAIN METRICS
            # =================================================

            a, b, c = st.columns(3)

            a.metric(
                "Predicted Rainfall",
                f"{pred:.2f} mm"
            )

            b.metric(
                "Weather",
                result["condition"]
            )

            c.metric(
                "ET0",
                f"{result['et0']:.2f}"
            )

            # =================================================
            # PROBABILITY MESSAGE
            # =================================================

            if probability < 20:

                st.info(
                    "☀️ Low rainfall likelihood."
                )

            elif probability < 50:

                st.info(
                    "🌤️ Moderate rainfall likelihood."
                )

            elif probability < 75:

                st.warning(
                    "🌧️ High rainfall likelihood."
                )

            else:

                st.success(
                    "⛈️ Very high rainfall likelihood."
                )

            # =================================================
            # GENERAL MESSAGE
            # =================================================

            st.info(
                result["message"]
            )

            st.caption(
                result["history_note"]
            )

            # =================================================
            # FUTURE MESSAGE
            # =================================================

            if result.get(
                "is_future",
                False
            ):

                st.success(
                    "🔮 Future prediction completed. "
                    "Previous rainfall data was used "
                    "for rain lag and rolling rainfall "
                    "features when available."
                )

            else:

                st.success(
                    "🌱 This prediction can be used "
                    "on the Agriculture page."
                )