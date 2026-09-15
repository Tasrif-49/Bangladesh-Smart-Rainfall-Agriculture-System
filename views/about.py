import streamlit as st


def show_about():


    st.title(

        "ℹ️ About System"

    )


    st.markdown(

        """

        ### 🌧️ Bangladesh Rainfall Prediction System

        **Model:** CatBoost Regression

        **Prediction Target:** Daily Rainfall (mm)

        **Features:**
        Weather, Calendar, Lag, Rolling & Station Features


        ---

        ### 🌱 Smart Agriculture System

        এই অংশে ব্যবহারকারী জানতে পারবেন:

        - 🌾 কোন ফসল কত পানি চায়

        - 📐 জমির পরিমাণ অনুযায়ী মোট পানি

        - 🌧️ predicted rainfall অনুযায়ী সেচ কমবে কিনা

        - 💧 আগে থেকে থাকা পানি বিবেচনা

        - 🟫 মাটির ধরন অনুযায়ী পানি

        - 🌱 crop growth stage অনুযায়ী পানি

        - 💨 ET0 অনুযায়ী পানির চাহিদা

        - 🚿 irrigation efficiency অনুযায়ী সেচ


        ---

        ### 🤖 Machine Learning

        এই system CatBoost Regression model ব্যবহার করে
        daily rainfall prediction করে।


        ---

        ### 👨‍💻 Developed By

        **Shams, Tasrif & Jishan**

        """

    )