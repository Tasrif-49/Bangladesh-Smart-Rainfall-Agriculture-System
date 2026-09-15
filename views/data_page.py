import streamlit as st
import pandas as pd


def show_data_page(df):

    st.title(
        "📂 Historical Weather Dataset"
    )

    # ============================================================
    # ENSURE DATE FORMAT
    # ============================================================

    df = df.copy()

    df["Date"] = pd.to_datetime(
        df["Date"],
        errors="coerce"
    ).dt.normalize()

    df = df.dropna(
        subset=["Date"]
    ).copy()

    # ============================================================
    # DATASET SUMMARY
    # ============================================================

    min_date = df["Date"].min().date()
    max_date = df["Date"].max().date()

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Records",
        f"{len(df):,}"
    )

    c2.metric(
        "Stations",
        df["Station_ID"].nunique()
    )

    c3.metric(
        "Period",
        f"{min_date.strftime('%d/%m/%Y')} → "
        f"{max_date.strftime('%d/%m/%Y')}"
    )

    # ============================================================
    # FILTERS
    # ============================================================

    s1, s2, s3 = st.columns(3)

    station = s1.selectbox(
        "Station",
        ["All"] + sorted(
            df["Station"]
            .astype(str)
            .unique()
            .tolist()
        ),
        key="historical_station"
    )

    division = s2.selectbox(
        "Division",
        ["All"] + sorted(
            df["Division"]
            .astype(str)
            .unique()
            .tolist()
        ),
        key="historical_division"
    )

    # ============================================================
    # DATE RANGE
    # ============================================================

    dates = s3.date_input(
        "📅 Date Range",
        value=(
            min_date,
            max_date
        ),
        key="historical_date_range",
        format="DD/MM/YYYY"
    )

    # ============================================================
    # APPLY FILTERS
    # ============================================================

    x = df.copy()

    if station != "All":

        x = x[
            x["Station"].astype(str)
            == station
        ]

    if division != "All":

        x = x[
            x["Division"].astype(str)
            == division
        ]

    # ============================================================
    # DATE FILTER
    # ============================================================

    if isinstance(dates, (tuple, list)):

        if len(dates) == 2:

            start_date = pd.Timestamp(
                dates[0]
            ).normalize()

            end_date = (
                pd.Timestamp(
                    dates[1]
                ).normalize()
                + pd.Timedelta(days=1)
            )

            x = x[
                (x["Date"] >= start_date)
                &
                (x["Date"] < end_date)
            ]

    elif dates is not None:

        selected = pd.Timestamp(
            dates
        ).normalize()

        x = x[
            x["Date"] == selected
        ]

    # ============================================================
    # DISPLAY FILTERED DATA
    # ============================================================

    st.caption(
        f"Showing {len(x):,} records"
    )

    st.dataframe(
        x,
        width="stretch",
        height=480
    )