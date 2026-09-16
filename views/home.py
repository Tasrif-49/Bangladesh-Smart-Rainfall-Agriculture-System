import streamlit as st
import pandas as pd
import plotly.express as px


def show_home(df):


    st.markdown(

        f"""

        <div class='hero'>

        <h1>
        🌧️ Bangladesh Smart Rainfall & Agriculture System
        </h1>

        <p>
        Rainfall prediction, agricultural water calculation
        and smart irrigation recommendation system.
        </p>

        <div class='hero-stats'>

        <div class='hero-stat'>

        <div class='hero-num'>
        {len(df):,}
        </div>

        <div class='hero-label'>
        Weather Records
        </div>

        </div>


        <div class='hero-stat'>

        <div class='hero-num'>
        {df.Station_ID.nunique()}
        </div>

        <div class='hero-label'>
        Weather Stations
        </div>

        </div>


        <div class='hero-stat'>

        <div class='hero-num'>
        CatBoost
        </div>

        <div class='hero-label'>
        Rainfall Model
        </div>

        </div>


        <div class='hero-stat'>

        <div class='hero-num'>
        🌱 Smart
        </div>

        <div class='hero-label'>
        Irrigation System
        </div>

        </div>

        </div>

        </div>

        """,

        unsafe_allow_html=True

    )


    st.markdown(

        "<div class='section-title'>🚀 Quick Access</div>",

        unsafe_allow_html=True

    )


    a, b, c = st.columns(3)


    if a.button(

        "🔮 Rainfall Prediction",

        width="stretch",

        type="primary"

    ):

        st.session_state.page = "🔮 Rain Prediction"

        st.rerun()


    if b.button(

        "🌱 Smart Agriculture (কৃষি সেচ ব্যবস্থা)",

       width="stretch",

        type="primary"

    ):

        st.session_state.page = "🌱 Agriculture "

        st.rerun()


    if c.button(

        "📊 Analytics",

       width="stretch",

        type="primary"

    ):

        st.session_state.page = "📊 Analytics"

        st.rerun()


    st.divider()


    left, right = st.columns(

        [1.5, 1]

    )


    with left:


        monthly = (

            df

            .assign(

                Month=df["Date"].dt.month

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


        fig = px.area(

            monthly,

            x="Month Name",

            y="Average Rainfall",

            title="Monthly Rainfall Pattern"

        )


        fig.update_yaxes(

            title="Rainfall (mm)"

        )


        fig.update_layout(
            height=400,
            dragmode=False,
            hovermode="closest",
            uirevision="constant"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": True,
                "displaylogo": False,
                "scrollZoom": False,
                "doubleClick": "reset",
                "modeBarButtonsToRemove": [
                    "pan2d",
                    "select2d",
                    "lasso2d",
                    "zoomIn2d",
                    "zoomOut2d"
                ]
            },
            key="monthly_rainfall_fixed"
        )


    with right:


        latest = (

            df

            .sort_values("Date")

            .tail(1000)

        )


        fig = px.histogram(

            latest,

            x="rain_sum",

            nbins=30,

            title="Rainfall Distribution"

        )


        fig.update_layout(
            height=400,
            dragmode=False,
            hovermode="closest",
            uirevision="constant"
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": True,
                "displaylogo": False,
                "scrollZoom": False,
                "doubleClick": "reset",
                "modeBarButtonsToRemove": [
                    "pan2d",
                    "select2d",
                    "lasso2d",
                    "zoomIn2d",
                    "zoomOut2d"
                ]
            },
            key="rainfall_distribution_fixed"
        )