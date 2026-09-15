import streamlit as st
import pandas as pd
import plotly.express as px

from services.agriculture import (

    CROPS,

    SOIL_TYPES,

    WATER_DEPTH_OPTIONS,

    convert_area_to_m2,

    convert_water_depth_to_mm,

    calculate_existing_water_volume,

    calculate_irrigation

)


def show_agriculture():


    # ========================================================
    # TITLE
    # ========================================================

    st.title(
        "Smart Agriculture & Irrigation"
    )


    st.caption(
        "ফসল, জমির পরিমাণ, মাটির ধরন, বৃষ্টির পূর্বাভাস এবং জমিতে থাকা পানি অনুযায়ী সেচের পানি হিসাব করুন।"
    )


    st.markdown(

        """
        <div class='agri-card'>

        <h3>
        Smart Irrigation Recommendation
        </h3>

        <p>
        ফসলের পানির প্রয়োজন, মাটির ধরন, ফসলের বৃদ্ধি পর্যায়,
        জমির পরিমাণ, বৃষ্টির পূর্বাভাস এবং ET0 ব্যবহার করে
        প্রয়োজনীয় সেচের পরিমাণ হিসাব করা হবে।
        </p>

        </div>
        """,

        unsafe_allow_html=True

    )


    # ========================================================
    # WEATHER INFORMATION
    # ========================================================

    st.markdown(

        "<div class='section-title'>আবহাওয়া ও বৃষ্টির তথ্য (Weather & Rainfall Information)</div>",

        unsafe_allow_html=True

    )


    weather_source = st.radio(

        "বৃষ্টির তথ্যের উৎস (Rainfall Source)",

        [

            "বৃষ্টির পূর্বাভাস ব্যবহার করুন (Use Rain Prediction)",

            "নিজে বৃষ্টির পরিমাণ দিন (Manual Rainfall Input)"

        ]

    )


    predicted_rain = 0.0

    et0_value = 0.0


    # ========================================================
    # PREDICTION SOURCE
    # ========================================================

    if weather_source.startswith(
        "বৃষ্টির পূর্বাভাস"
    ):


        if (
            "rain_prediction"
            in
            st.session_state
        ):


            rain_data = (
                st.session_state.rain_prediction
            )


            predicted_rain = (
                rain_data.get(
                    "prediction",
                    0.0
                )
            )


            et0_value = (
                rain_data.get(
                    "et0",
                    4.0
                )
            )


            st.success(

                f"""
                বৃষ্টির পূর্বাভাস (Predicted Rainfall): {predicted_rain:.2f} mm

                ET0 (Evapotranspiration): {et0_value:.2f}
                """

            )


        else:


            st.warning(

                "আগে Rain Prediction করুন অথবা নিজে বৃষ্টির পরিমাণ দিন নির্বাচন করুন।"

            )


            c1, c2 = st.columns(2)


            predicted_rain = c1.number_input(

                "আজকের বৃষ্টির পরিমাণ (Today's Rainfall) mm",

                min_value=0.0,

                value=0.0,

                step=0.5

            )


            et0_value = c2.number_input(

                "বাষ্পীভবন হার (ET0 / Evapotranspiration)",

                min_value=0.0,

                value=4.0,

                step=0.1

            )


    # ========================================================
    # MANUAL SOURCE
    # ========================================================

    else:


        c1, c2 = st.columns(2)


        predicted_rain = c1.number_input(

            "আজকের বৃষ্টির পরিমাণ (Today's Rainfall) mm",

            min_value=0.0,

            value=0.0,

            step=0.5

        )


        et0_value = c2.number_input(

            "বাষ্পীভবন হার (ET0 / Evapotranspiration)",

            min_value=0.0,

            value=4.0,

            step=0.1

        )


    # ========================================================
    # LAND INFORMATION
    # ========================================================

    st.markdown(

        "<div class='section-title'>জমির তথ্য (Land Information)</div>",

        unsafe_allow_html=True

    )


    c1, c2 = st.columns(2)


    land_area = c1.number_input(

        "জমির পরিমাণ (Land Area)",

        min_value=0.01,

        value=1.0,

        step=0.01

    )


    area_unit = c2.selectbox(

        "জমির একক (Area Unit)",

        [

            "শতক (Decimal)",

            "একর (Acre)",

            "হেক্টর (Hectare)",

            "বর্গমিটার (Square Meter)"

        ]

    )


    # ========================================================
    # CROP INFORMATION
    # ========================================================

    st.markdown(

        "<div class='section-title'>ফসলের তথ্য (Crop Information)</div>",

        unsafe_allow_html=True

    )


    c1, c2 = st.columns(2)


    crop_name = c1.selectbox(

        "ফসল নির্বাচন করুন (Select Crop)",

        list(
            CROPS.keys()
        )

    )


    crop_stage = c2.selectbox(

        "ফসলের বৃদ্ধি পর্যায় (Crop Growth Stage)",

        list(
            CROPS[crop_name][
                "stage_factor"
            ].keys()
        )

    )


    st.info(

        CROPS[crop_name][
            "description"
        ]

    )


    # ========================================================
    # SOIL INFORMATION
    # ========================================================

    st.markdown(

        "<div class='section-title'>মাটির তথ্য (Soil Information)</div>",

        unsafe_allow_html=True

    )


    c1, c2 = st.columns(2)


    soil_type = c1.selectbox(

        "মাটির ধরন (Soil Type)",

        list(
            SOIL_TYPES.keys()
        )

    )


    st.caption(

        SOIL_TYPES[soil_type][
            "description"
        ]

    )


    # ========================================================
    # EXISTING WATER
    # ========================================================

    st.markdown(

        "<div class='section-title'>জমিতে আগে থেকে থাকা পানি (Existing Water)</div>",

        unsafe_allow_html=True

    )


    st.info(

        """
        জমিতে কত মিলিমিটার পানি আছে তা সরাসরি জানা কঠিন।

        তাই আপনি আঙুল দিয়ে পানির গভীরতা মাপতে পারেন।
        সিস্টেম সেই পরিমাপকে আনুমানিক মিলিমিটারে পরিবর্তন করবে।

        এটি একটি আনুমানিক হিসাব।
        """

    )


    water_measurement = st.selectbox(

        "পানির গভীরতা নির্বাচন করুন (Select Water Depth)",

        list(
            WATER_DEPTH_OPTIONS.keys()
        )

        +

        [
            "নিজে পরিমাপ দিন (Custom Measurement)"
        ]

    )


    custom_depth_cm = 0.0


    if water_measurement == "নিজে পরিমাপ দিন (Custom Measurement)":


        custom_depth_cm = st.number_input(

            "পানির গভীরতা সেন্টিমিটারে দিন (Water Depth in cm)",

            min_value=0.0,

            value=0.0,

            step=0.5

        )


    existing_water_mm = convert_water_depth_to_mm(

        water_measurement,

        custom_depth_cm

    )


    # ========================================================
    # EXISTING WATER CALCULATION
    # ========================================================

    area_m2_preview = convert_area_to_m2(

        land_area,

        area_unit

    )


    existing_water_volume = calculate_existing_water_volume(

        area_m2_preview,

        existing_water_mm

    )


    # ========================================================
    # WATER ESTIMATE DISPLAY
    # ========================================================

    st.markdown(

        "<div class='section-title'>আনুমানিক পানির হিসাব (Estimated Water Calculation)</div>",

        unsafe_allow_html=True

    )


    a, b, c = st.columns(3)


    a.metric(

        "আনুমানিক পানির গভীরতা (Estimated Water Depth)",

        f"{existing_water_mm:.1f} mm"

    )


    b.metric(

        "আনুমানিক মোট পানি (Estimated Total Water)",

        f"{existing_water_volume['water_liters']:,.0f} L"

    )


    c.metric(

        "আনুমানিক পানির পরিমাণ (Estimated Water Volume)",

        f"{existing_water_volume['water_m3']:.2f} m³"

    )


    st.caption(

        "নোট: আঙুল দিয়ে মাপার কারণে এটি আনুমানিক হিসাব। প্রকৃত পানির গভীরতা ও পরিমাণ কিছুটা ভিন্ন হতে পারে।"

    )


    # ========================================================
    # IRRIGATION SYSTEM
    # ========================================================

    st.markdown(

        "<div class='section-title'>সেচ ব্যবস্থা (Irrigation System)</div>",

        unsafe_allow_html=True

    )


    irrigation_method = st.selectbox(

        "সেচ পদ্ধতি নির্বাচন করুন (Select Irrigation Method)",

        [

            "সাধারণ সেচ (Traditional Irrigation)",

            "স্প্রিংকলার (Sprinkler)",

            "ড্রিপ সেচ (Drip Irrigation)"

        ]

    )


    if irrigation_method.startswith(
        "সাধারণ"
    ):

        default_efficiency = 60


    elif irrigation_method.startswith(
        "স্প্রিংকলার"
    ):

        default_efficiency = 75


    else:

        default_efficiency = 90


    irrigation_efficiency = st.slider(

        "সেচ দক্ষতা (Irrigation Efficiency %)",

        min_value=30,

        max_value=100,

        value=default_efficiency

    )


    # ========================================================
    # CALCULATE BUTTON
    # ========================================================

    if st.button(

        "স্মার্ট সেচ হিসাব করুন (Calculate Smart Irrigation)",

        type="primary",

        width="stretch"

    ):


        result = calculate_irrigation(

            land_area=land_area,

            area_unit=area_unit,

            crop_name=crop_name,

            crop_stage=crop_stage,

            soil_type=soil_type,

            existing_water_mm=existing_water_mm,

            predicted_rain_mm=predicted_rain,

            et0_value=et0_value,

            irrigation_efficiency=irrigation_efficiency

        )


        st.session_state.agri_result = {

            "result": result,

            "crop_name": crop_name,

            "crop_stage": crop_stage,

            "soil_type": soil_type,

            "predicted_rain": predicted_rain,

            "existing_water": existing_water_mm,

            "existing_water_liters":
                existing_water_volume["water_liters"],

            "existing_water_m3":
                existing_water_volume["water_m3"],

            "water_measurement":
                water_measurement,

            "et0": et0_value,

            "land_area": land_area,

            "area_unit": area_unit,

            "irrigation_method": irrigation_method,

            "efficiency": irrigation_efficiency

        }


    # ========================================================
    # RESULT
    # ========================================================

    if (
        "agri_result"
        in
        st.session_state
    ):


        data = (
            st.session_state.agri_result
        )


        result = data["result"]


        st.divider()


        st.subheader(

            "স্মার্ট সেচের ফলাফল (Smart Irrigation Result)"

        )


        st.markdown(

            f"""

            <div class='result-card'>

            <h2>
            {result['status_bn']}
            </h2>

            <h3>
            {result['status_en']}
            </h3>

            </div>

            """,

            unsafe_allow_html=True

        )


        # ====================================================
        # WATER REQUIREMENT
        # ====================================================

        a, b, c, d = st.columns(4)


        a.metric(

            "ফসলের পানির চাহিদা (Crop Water Need)",

            f"{result['crop_water_need']:.2f} mm"

        )


        b.metric(

            "কার্যকর বৃষ্টির পানি (Effective Rain)",

            f"{result['effective_rain']:.2f} mm"

        )


        c.metric(

            "মোট প্রয়োজনীয় পানি (Net Water Need)",

            f"{result['net_water_needed']:.2f} mm"

        )


        d.metric(

            "প্রয়োজনীয় সেচের পানি (Irrigation Water)",

            f"{result['gross_water_mm']:.2f} mm"

        )


        # ====================================================
        # WATER VOLUME
        # ====================================================

        st.markdown(

            "<div class='section-title'>কতটুকু পানি প্রয়োজন (How Much Water)</div>",

            unsafe_allow_html=True

        )


        a, b, c = st.columns(3)


        a.metric(

            "লিটার (Liters)",

            f"{result['water_liters']:,.0f} L"

        )


        b.metric(

            "ঘনমিটার (Cubic Meter)",

            f"{result['water_m3']:,.2f} m³"

        )


        c.metric(

            "জমির আয়তন (Land Area)",

            f"{result['area_m2']:,.0f} m²"

        )


        # ====================================================
        # EXISTING WATER RESULT
        # ====================================================

        st.markdown(

            "<div class='section-title'>জমিতে থাকা পানির তথ্য (Existing Water Information)</div>",

            unsafe_allow_html=True

        )


        a, b, c = st.columns(3)


        a.metric(

            "পানির গভীরতা (Water Depth)",

            f"{data['existing_water']:.1f} mm"

        )


        b.metric(

            "আনুমানিক মোট পানি (Estimated Total Water)",

            f"{data['existing_water_liters']:,.0f} L"

        )


        c.metric(

            "আনুমানিক পানির পরিমাণ (Estimated Volume)",

            f"{data['existing_water_m3']:.2f} m³"

        )


        st.caption(

            f"ব্যবহৃত পরিমাপ: {data['water_measurement']}। এটি একটি আনুমানিক হিসাব।"

        )


        # ====================================================
        # SMART RECOMMENDATION
        # ====================================================

        st.markdown(

            "<div class='section-title'>স্মার্ট পরামর্শ (Smart Recommendation)</div>",

            unsafe_allow_html=True

        )


        recommendations = []


        if result["status"] == "NO_IRRIGATION":


            recommendations.append(

                "আজ অতিরিক্ত সেচ দেওয়ার প্রয়োজন নেই (No additional irrigation is needed today)।"

            )


            recommendations.append(

                "জমিতে থাকা পানি এবং কার্যকর বৃষ্টির পানি ফসলের বর্তমান চাহিদার জন্য যথেষ্ট।"

            )


        elif result["status"] == "LOW":


            recommendations.append(

                "অল্প পরিমাণ সেচ দিন (Light irrigation is recommended)।"

            )


        elif result["status"] == "MEDIUM":


            recommendations.append(

                "মাঝারি পরিমাণ সেচ দেওয়া ভালো হবে (Moderate irrigation is recommended)।"

            )


        else:


            recommendations.append(

                "আজ ফসলের পানির চাহিদা বেশি। পর্যাপ্ত সেচ দিন (High irrigation requirement)।"

            )


        # RAIN RECOMMENDATION

        if predicted_rain >= 20:


            recommendations.append(

                "বৃষ্টির পরিমাণ বেশি হতে পারে। সেচ দেওয়ার আগে বৃষ্টির পরিস্থিতি বিবেচনা করুন।"

            )


        # EXISTING WATER RECOMMENDATION

        if existing_water_mm >= result["crop_water_need"]:


            recommendations.append(

                "জমিতে আগে থেকেই পর্যাপ্ত পানি আছে। অতিরিক্ত পানি জমে থাকলে ফসলের ক্ষতি হতে পারে।"

            )


        # SANDY SOIL

        if data["soil_type"].startswith(
            "বেলে"
        ):


            recommendations.append(

                "বেলে মাটিতে পানি দ্রুত নিচে চলে যায়। প্রয়োজন হলে একবারে বেশি পানি না দিয়ে ভাগ করে সেচ দিন।"

            )


        # CLAY SOIL

        if data["soil_type"].startswith(
            "এঁটেল"
        ):


            recommendations.append(

                "এঁটেল মাটি পানি বেশি সময় ধরে রাখে। সেচ দেওয়ার আগে জমিতে পানি জমে আছে কিনা পরীক্ষা করুন।"

            )


        # DRIP

        if data["irrigation_method"].startswith(
            "ড্রিপ"
        ):


            recommendations.append(

                "ড্রিপ সেচ পানি সাশ্রয়ে কার্যকর এবং নিয়ন্ত্রিতভাবে পানি সরবরাহ করতে সাহায্য করে।"

            )


        for rec in recommendations:

            st.write(
                rec
            )


        # ====================================================
        # WATER BALANCE CHART
        # ====================================================

        chart_df = pd.DataFrame({

            "বিভাগ (Category)": [

                "ফসলের চাহিদা (Crop Need)",

                "জমিতে থাকা পানি (Existing Water)",

                "কার্যকর বৃষ্টি (Effective Rain)",

                "প্রয়োজনীয় সেচ (Irrigation Needed)"

            ],


            "পানি (Water mm)": [

                result["crop_water_need"],

                data["existing_water"],

                result["effective_rain"],

                result["gross_water_mm"]

            ]

        })


        fig = px.bar(

            chart_df,

            x="বিভাগ (Category)",

            y="পানি (Water mm)",

            title="কৃষি পানির ভারসাম্য (Agricultural Water Balance)",

            text_auto=".2f"

        )


        fig.update_layout(

            xaxis_title="",

            yaxis_title="পানির পরিমাণ (Water in mm)"

        )


        st.plotly_chart(

            fig,

            width="stretch"

        )