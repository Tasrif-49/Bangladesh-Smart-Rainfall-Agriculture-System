import streamlit as st
import pandas as pd
import plotly.express as px


def show_analytics(df):


    st.title(

        "📊 Advanced Analytics"

    )


    stations = sorted(

        df.Station.astype(str).unique()

    )


    sel = st.selectbox(

        "Station for detailed analytics",

        ["All"]

        +

        stations

    )


    if sel == "All":

        x = df.copy()


    else:

        x = df[

            df.Station.astype(str)

            ==

            sel

        ].copy()


    if x.empty:


        st.warning(

            "No data available."

        )


        return


    # ========================================================
    # MONTHLY
    # ========================================================

    monthly = (

        x

        .assign(

            Month=x["Date"].dt.month

        )

        .groupby(

            "Month",

            as_index=False

        )["rain_sum"]

        .mean()

        .rename(

            columns={

                "rain_sum":
                "Average Rainfall"

            }

        )

    )


    monthly["Month Name"] = (

        pd.to_datetime(

            monthly["Month"],

            format="%m"

        )

        .dt.strftime("%b")

    )


    fig = px.bar(

        monthly,

        x="Month Name",

        y="Average Rainfall",

        title="Monthly Average Rainfall"

    )


    st.plotly_chart(

        fig,

       width="stretch"
    )


    # ========================================================
    # SAMPLE
    # ========================================================

    sample = x.sample(

        min(

            3000,

            len(x)

        ),

        random_state=42

    )


    a, b = st.columns(2)


    with a:


        fig = px.line(

            x

            .sort_values("Date")

            .tail(1000),

            x="Date",

            y="rain_sum",

            title="Historical Rainfall Trend"

        )


        st.plotly_chart(

            fig,

           width="stretch"

        )


    with b:


        fig = px.scatter(

            sample,

            x="temperature_2m_mean",

            y="rain_sum",

            title="Temperature vs Rainfall"

        )


        st.plotly_chart(

            fig,

           width="stretch"

        )


    a, b = st.columns(2)


    with a:


        fig = px.scatter(

            sample,

            x="wind_speed_10m_max",

            y="rain_sum",

            title="Wind Speed vs Rainfall"

        )


        st.plotly_chart(

            fig,

           width="stretch"

        )


    with b:


        fig = px.histogram(

            x,

            x="rain_sum",

            nbins=50,

            title="Rainfall Distribution"

        )


        st.plotly_chart(

            fig,

           width="stretch"

        )


    # ========================================================
    # STATION AVERAGE
    # ========================================================

    station_avg = (

        df

        .groupby(

            "Station",

            as_index=False

        )["rain_sum"]

        .mean()

        .sort_values(

            "rain_sum",

            ascending=False

        )

        .head(20)

    )


    fig = px.bar(

        station_avg,

        x="Station",

        y="rain_sum",

        title="Top 20 Stations by Average Rainfall"

    )


    st.plotly_chart(

        fig,

       width="stretch"

    )