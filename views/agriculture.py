import re

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
    calculate_irrigation,
)


# ============================================================
# বাংলা UI সহায়ক ফাংশন
# ============================================================

BN_DIGIT_TABLE = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")


def bn_digits(value):
    """ইংরেজি সংখ্যাকে বাংলা সংখ্যায় দেখানোর জন্য।"""
    return str(value).translate(BN_DIGIT_TABLE)


def bn_num(value, decimals=0, comma=False):
    """সংখ্যা format করে বাংলা digit-এ দেখায়।"""
    if comma:
        text = f"{value:,.{decimals}f}"
    else:
        text = f"{value:.{decimals}f}"
    return bn_digits(text)




def bn_streamlit_input(label, default=0.0, key="bn_input"):
    if key not in st.session_state:
        st.session_state[key] = bn_digits(f"{default:.2f}")

    def convert():
        value = st.session_state[key]
        st.session_state[key] = bn_digits(str(value))

    value = st.text_input(label, key=key, on_change=convert)

    try:
        return float(str(value).translate(
            str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
        ))
    except:
        return default



def bangla_all_numeric_input(label, default=0.0, key="bn_all_input", step=0.01):
    """
    Streamlit friendly numeric input.
    Keeps layout unchanged and converts English digits to Bangla display.
    """
    if key not in st.session_state:
        st.session_state[key] = bn_digits(f"{default:.2f}")

    def update_bn():
        value = st.session_state[key]
        st.session_state[key] = bn_digits(value)

    st.text_input(
        label,
        key=key,
        on_change=update_bn
    )

    value = st.session_state[key]

    try:
        return float(str(value).translate(
            str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
        ))
    except:
        return default


def remove_english_parentheses(text):
    """যেমন 'শতক (Decimal)' -> 'শতক'।"""
    text = str(text)
    text = re.sub(r"\s*\([^)]*[A-Za-z][^)]*\)", "", text)
    return text.strip()


# Backend key অপরিবর্তিত থাকবে, শুধু UI-তে বাংলা নাম দেখাবে।
BANGLA_VALUE_MAP = {
    # Crop names
    "Rice": "ধান",
    "Paddy": "ধান",
    "Wheat": "গম",
    "Maize": "ভুট্টা",
    "Corn": "ভুট্টা",
    "Potato": "আলু",
    "Tomato": "টমেটো",
    "Brinjal": "বেগুন",
    "Eggplant": "বেগুন",
    "Mustard": "সরিষা",
    "Onion": "পেঁয়াজ",
    "Garlic": "রসুন",
    "Chili": "মরিচ",
    "Chilli": "মরিচ",
    "Jute": "পাট",
    "Sugarcane": "আখ",
    "Lentil": "মসুর ডাল",
    "Pulse": "ডাল",
    "Soybean": "সয়াবিন",
    "Groundnut": "চিনাবাদাম",
    "Peanut": "চিনাবাদাম",
    "Cucumber": "শসা",
    "Pumpkin": "কুমড়া",
    "Watermelon": "তরমুজ",
    "Cabbage": "বাঁধাকপি",
    "Cauliflower": "ফুলকপি",
    "Okra": "ঢেঁড়স",
    "Bean": "শিম",
    "Beans": "শিম",

    # Crop growth stages
    "Initial": "প্রাথমিক পর্যায়",
    "Initial Stage": "প্রাথমিক পর্যায়",
    "Seedling": "চারা পর্যায়",
    "Seedling Stage": "চারা পর্যায়",
    "Development": "বৃদ্ধি পর্যায়",
    "Development Stage": "বৃদ্ধি পর্যায়",
    "Vegetative": "অঙ্গজ বৃদ্ধি পর্যায়",
    "Vegetative Stage": "অঙ্গজ বৃদ্ধি পর্যায়",
    "Flowering": "ফুল আসার পর্যায়",
    "Flowering Stage": "ফুল আসার পর্যায়",
    "Fruiting": "ফল ধরার পর্যায়",
    "Fruiting Stage": "ফল ধরার পর্যায়",
    "Mid": "মধ্য পর্যায়",
    "Mid Season": "মধ্য মৌসুম",
    "Mid-season": "মধ্য মৌসুম",
    "Late": "শেষ পর্যায়",
    "Late Season": "শেষ মৌসুম",
    "Late-season": "শেষ মৌসুম",
    "Maturity": "পরিপক্বতার পর্যায়",
    "Maturity Stage": "পরিপক্বতার পর্যায়",
    "Harvest": "ফসল তোলার পর্যায়",

    # Soil types
    "Sandy": "বেলে মাটি",
    "Sandy Soil": "বেলে মাটি",
    "Loamy": "দোআঁশ মাটি",
    "Loam": "দোআঁশ মাটি",
    "Loamy Soil": "দোআঁশ মাটি",
    "Silty": "পলিমাটি",
    "Silt": "পলিমাটি",
    "Clay": "এঁটেল মাটি",
    "Clay Soil": "এঁটেল মাটি",
    "Clayey": "এঁটেল মাটি",
    "Sandy Loam": "বেলে দোআঁশ মাটি",
    "Clay Loam": "এঁটেল দোআঁশ মাটি",
    "Silty Loam": "পলি দোআঁশ মাটি",

    # Water depth / moisture options
    "Dry": "শুকনা",
    "Very Dry": "খুব শুকনা",
    "Slightly Wet": "সামান্য ভেজা",
    "Moist": "আর্দ্র",
    "Wet": "ভেজা",
    "Very Wet": "খুব ভেজা",
    "Waterlogged": "পানি জমে আছে",
    "No Water": "পানি নেই",
    "Low": "কম",
    "Medium": "মাঝারি",
    "High": "বেশি",
}


def bangla_value_label(value):
    """Selectbox/radio-র value শুধু UI-তে বাংলায় দেখায়।"""
    text = str(value).strip()

    if text in BANGLA_VALUE_MAP:
        return BANGLA_VALUE_MAP[text]

    # আগে থেকেই বাংলা + English bracket থাকলে English অংশ সরিয়ে দিন
    cleaned = remove_english_parentheses(text)
    if cleaned != text:
        return cleaned

    # case-insensitive fallback
    lowered = text.casefold()
    for key, bn_text in BANGLA_VALUE_MAP.items():
        if lowered == key.casefold():
            return bn_text

    return text


def bangla_description(text):
    """Mixed Bangla-English description হলে bracket-এর English অংশ বাদ দেয়।"""
    return remove_english_parentheses(text)


# ============================================================
# মূল পেজ
# ============================================================

def show_agriculture():

    # ========================================================
    # শিরোনাম
    # ========================================================

    st.title("স্মার্ট কৃষি ও সেচ")

    st.caption(
        "ফসল, জমির পরিমাণ, মাটির ধরন, বৃষ্টির পূর্বাভাস এবং জমিতে থাকা পানি অনুযায়ী সেচের পানি হিসাব করুন।"
    )

    st.markdown(
        """
        <div class='agri-card'>
            <h3>স্মার্ট সেচ পরামর্শ</h3>
            <p>
            ফসলের পানির প্রয়োজন, মাটির ধরন, ফসলের বৃদ্ধি পর্যায়,
            জমির পরিমাণ, বৃষ্টির পূর্বাভাস এবং বাষ্পীভবন হার ব্যবহার করে
            প্রয়োজনীয় সেচের পরিমাণ হিসাব করা হবে।
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ========================================================
    # আবহাওয়া ও বৃষ্টির তথ্য
    # ========================================================

    st.markdown(
        "<div class='section-title'>আবহাওয়া ও বৃষ্টির তথ্য</div>",
        unsafe_allow_html=True,
    )

    weather_source = st.radio(
        "বৃষ্টির তথ্যের উৎস",
        [
            "বৃষ্টির পূর্বাভাস ব্যবহার করুন",
            "নিজে বৃষ্টির পরিমাণ দিন",
        ],
    )

    predicted_rain = 0.0
    et0_value = 0.0

    # ========================================================
    # পূর্বাভাস থেকে তথ্য
    # ========================================================

    if weather_source == "বৃষ্টির পূর্বাভাস ব্যবহার করুন":

        if "rain_prediction" in st.session_state:
            rain_data = st.session_state.rain_prediction
            predicted_rain = rain_data.get("prediction", 0.0)
            et0_value = rain_data.get("et0", 4.0)

            st.success(
                f"বৃষ্টির পূর্বাভাস: {bn_num(predicted_rain, 2)} মিমি\n\n"
                f"বাষ্পীভবন হার: {bn_num(et0_value, 2)}"
            )

        else:
            st.warning(
                "আগে বৃষ্টির পূর্বাভাস তৈরি করুন অথবা ‘নিজে বৃষ্টির পরিমাণ দিন’ নির্বাচন করুন।"
            )

            c1, c2 = st.columns(2)

            predicted_rain = c1.empty()
            predicted_rain = bn_streamlit_input(
                "আজকের বৃষ্টির পরিমাণ (মিমি)",
                default=0.0,
                key="rain_bn"
            )

            et0_value = c2.empty()
            et0_value = bn_streamlit_input(
                "বাষ্পীভবন হার",
                default=4.0,
                key="et0_bn"
            )

    # ========================================================
    # নিজে তথ্য দেওয়া
    # ========================================================

    else:
        c1, c2 = st.columns(2)

        with c1:
            predicted_rain = bangla_all_numeric_input(
                "আজকের বৃষ্টির পরিমাণ (মিমি)",
                default=0.0,
                key="rain_all_bn"
            )

        with c2:
            et0_value = bangla_all_numeric_input(
                "বাষ্পীভবন হার",
                default=4.0,
                key="et0_all_bn"
            )

    # ========================================================
    # জমির তথ্য
    # ========================================================

    st.markdown(
        "<div class='section-title'>জমির তথ্য</div>",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)

    with c1:
        land_area = bn_streamlit_input(
            "জমির পরিমাণ",
            default=1.0,
            key="land_area_bn"
        )

    with c2:
        # backend-এর original string রাখা হয়েছে
        area_unit = st.selectbox(
            "জমির একক",
        [
            "শতক (Decimal)",
            "একর (Acre)",
            "হেক্টর (Hectare)",
            "বর্গমিটার (Square Meter)",
        ],
        format_func=bangla_value_label,
    )

    # ========================================================
    # ফসলের তথ্য
    # ========================================================

    st.markdown(
        "<div class='section-title'>ফসলের তথ্য</div>",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)

    # UI-তে বাংলা; backend-এ CROPS-এর original key
    crop_name = c1.selectbox(
        "ফসল নির্বাচন করুন",
        list(CROPS.keys()),
        format_func=bangla_value_label,
    )

    crop_stage = c2.selectbox(
        "ফসলের বৃদ্ধি পর্যায়",
        list(CROPS.get(crop_name, {}).get("stage_factor", {"Default": 1}).keys()),
        format_func=bangla_value_label,
    )

    crop_description = CROPS[crop_name].get("description", "")
    if crop_description:
        st.info(bangla_description(crop_description))

    # ========================================================
    # মাটির তথ্য
    # ========================================================

    st.markdown(
        "<div class='section-title'>মাটির তথ্য</div>",
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns(2)

    # UI-তে বাংলা; backend-এ SOIL_TYPES-এর original key
    soil_type = c1.selectbox(
        "মাটির ধরন",
        list(SOIL_TYPES.keys()),
        format_func=bangla_value_label,
    )

    soil_description = SOIL_TYPES[soil_type].get("description", "")
    if soil_description:
        st.caption(bangla_description(soil_description))

    # ========================================================
    # জমিতে আগে থেকে থাকা পানি
    # ========================================================

    st.markdown(
        "<div class='section-title'>জমিতে আগে থেকে থাকা পানি</div>",
        unsafe_allow_html=True,
    )

    st.info(
        """
        জমিতে কত মিলিমিটার পানি আছে তা সরাসরি জানা কঠিন।

        তাই আপনি আঙুল দিয়ে পানির গভীরতা মাপতে পারেন।
        সিস্টেম সেই পরিমাপকে আনুমানিক মিলিমিটারে পরিবর্তন করবে।

        এটি একটি আনুমানিক হিসাব।
        """
    )

    custom_water_key = "নিজে পরিমাপ দিন (Custom Measurement)"

    water_measurement = st.selectbox(
        "পানির গভীরতা নির্বাচন করুন",
        list(WATER_DEPTH_OPTIONS.keys()) + [custom_water_key],
        format_func=bangla_value_label,
    )

    custom_depth_cm = 0.0

    if water_measurement == custom_water_key:
        custom_depth_cm = bangla_all_numeric_input(
            "পানির গভীরতা সেন্টিমিটারে দিন",
            default=0.0,
            key="water_depth_all_bn"
        )

    existing_water_mm = convert_water_depth_to_mm(
        water_measurement,
        custom_depth_cm,
    )

    # ========================================================
    # জমিতে থাকা পানির হিসাব
    # ========================================================

    area_m2_preview = convert_area_to_m2(
        land_area,
        area_unit,
    )

    existing_water_volume = calculate_existing_water_volume(
        area_m2_preview,
        existing_water_mm,
    )

    # ========================================================
    # আনুমানিক পানির হিসাব
    # ========================================================

    st.markdown(
        "<div class='section-title'>আনুমানিক পানির হিসাব</div>",
        unsafe_allow_html=True,
    )

    a, b, c = st.columns(3)

    a.metric(
        "আনুমানিক পানির গভীরতা",
        f"{bn_num(existing_water_mm, 1)} মিমি",
    )

    b.metric(
        "আনুমানিক মোট পানি",
        f"{bn_num(existing_water_volume['water_liters'], 0, comma=True)} লিটার",
    )

    c.metric(
        "আনুমানিক পানির পরিমাণ",
        f"{bn_num(existing_water_volume['water_m3'], 2, comma=True)} ঘনমিটার",
    )

    st.caption(
        "নোট: আঙুল দিয়ে মাপার কারণে এটি আনুমানিক হিসাব। প্রকৃত পানির গভীরতা ও পরিমাণ কিছুটা ভিন্ন হতে পারে।"
    )

    # ========================================================
    # সেচ ব্যবস্থা
    # ========================================================

    st.markdown(
        "<div class='section-title'>সেচ ব্যবস্থা</div>",
        unsafe_allow_html=True,
    )

    # backend logic-এর জন্য existing Bangla prefix রাখা হয়েছে
    irrigation_method = st.selectbox(
        "সেচ পদ্ধতি নির্বাচন করুন",
        [
            "সাধারণ সেচ (Traditional Irrigation)",
            "স্প্রিংকলার (Sprinkler)",
            "ড্রিপ সেচ (Drip Irrigation)",
        ],
        format_func=bangla_value_label,
    )

    if irrigation_method.startswith("সাধারণ"):
        default_efficiency = 60
    elif irrigation_method.startswith("স্প্রিংকলার"):
        default_efficiency = 75
    else:
        default_efficiency = 90

    irrigation_efficiency = st.slider(
        "সেচ দক্ষতা (%)",
        min_value=30,
        max_value=100,
        value=default_efficiency,
    )

    st.caption(
        f"নির্বাচিত সেচ দক্ষতা: {bn_digits(irrigation_efficiency)}%"
    )

    # ========================================================
    # হিসাবের বোতাম
    # ========================================================

    if st.button(
        "স্মার্ট সেচ হিসাব করুন",
        type="primary",
        width="stretch",
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
            irrigation_efficiency=irrigation_efficiency,
        )

        st.session_state.agri_result = {
            "result": result,
            "crop_name": crop_name,
            "crop_stage": crop_stage,
            "soil_type": soil_type,
            "predicted_rain": predicted_rain,
            "existing_water": existing_water_mm,
            "existing_water_liters": existing_water_volume["water_liters"],
            "existing_water_m3": existing_water_volume["water_m3"],
            "water_measurement": water_measurement,
            "et0": et0_value,
            "land_area": land_area,
            "area_unit": area_unit,
            "irrigation_method": irrigation_method,
            "efficiency": irrigation_efficiency,
        }

    # ========================================================
    # ফলাফল
    # ========================================================

    if "agri_result" in st.session_state:
        data = st.session_state.agri_result
        result = data["result"]

        st.divider()
        st.subheader("স্মার্ট সেচের ফলাফল")

        st.markdown(
            f"""
            <div class='result-card'>
                <h2>{result.get("status_bn", result.get("status", ""))}</h2>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ====================================================
        # পানির প্রয়োজন
        # ====================================================

        a, b, c, d = st.columns(4)

        a.metric(
            "ফসলের পানির চাহিদা",
            f"{bn_num(result['crop_water_need'], 2)} মিমি",
        )

        b.metric(
            "কার্যকর বৃষ্টির পানি",
            f"{bn_num(result['effective_rain'], 2)} মিমি",
        )

        c.metric(
            "মোট প্রয়োজনীয় পানি",
            f"{bn_num(result['net_water_needed'], 2)} মিমি",
        )

        d.metric(
            "প্রয়োজনীয় সেচের পানি",
            f"{bn_num(result['gross_water_mm'], 2)} মিমি",
        )

        # ====================================================
        # কতটুকু পানি প্রয়োজন
        # ====================================================

        st.markdown(
            "<div class='section-title'>কতটুকু পানি প্রয়োজন</div>",
            unsafe_allow_html=True,
        )

        a, b, c = st.columns(3)

        a.metric(
            "লিটার",
            f"{bn_num(result['water_liters'], 0, comma=True)} লিটার",
        )

        b.metric(
            "ঘনমিটার",
            f"{bn_num(result['water_m3'], 2, comma=True)} ঘনমিটার",
        )

        c.metric(
            "জমির আয়তন",
            f"{bn_num(result['area_m2'], 0, comma=True)} বর্গমিটার",
        )

        # ====================================================
        # জমিতে থাকা পানির তথ্য
        # ====================================================

        st.markdown(
            "<div class='section-title'>জমিতে থাকা পানির তথ্য</div>",
            unsafe_allow_html=True,
        )

        a, b, c = st.columns(3)

        a.metric(
            "পানির গভীরতা",
            f"{bn_num(data['existing_water'], 1)} মিমি",
        )

        b.metric(
            "আনুমানিক মোট পানি",
            f"{bn_num(data['existing_water_liters'], 0, comma=True)} লিটার",
        )

        c.metric(
            "আনুমানিক পানির পরিমাণ",
            f"{bn_num(data['existing_water_m3'], 2, comma=True)} ঘনমিটার",
        )

        st.caption(
            f"ব্যবহৃত পরিমাপ: {bangla_value_label(data['water_measurement'])}। এটি একটি আনুমানিক হিসাব।"
        )

        # ====================================================
        # স্মার্ট পরামর্শ
        # ====================================================

        st.markdown(
            "<div class='section-title'>স্মার্ট পরামর্শ</div>",
            unsafe_allow_html=True,
        )

        recommendations = []

        if result["status"] == "NO_IRRIGATION":
            recommendations.append(
                "আজ অতিরিক্ত সেচ দেওয়ার প্রয়োজন নেই।"
            )
            recommendations.append(
                "জমিতে থাকা পানি এবং কার্যকর বৃষ্টির পানি ফসলের বর্তমান চাহিদার জন্য যথেষ্ট।"
            )

        elif result["status"] == "LOW":
            recommendations.append(
                "অল্প পরিমাণ সেচ দিন।"
            )

        elif result["status"] == "MEDIUM":
            recommendations.append(
                "মাঝারি পরিমাণ সেচ দেওয়া ভালো হবে।"
            )

        else:
            recommendations.append(
                "আজ ফসলের পানির চাহিদা বেশি। পর্যাপ্ত সেচ দিন।"
            )

        if predicted_rain >= 20:
            recommendations.append(
                "বৃষ্টির পরিমাণ বেশি হতে পারে। সেচ দেওয়ার আগে বৃষ্টির পরিস্থিতি বিবেচনা করুন।"
            )

        if existing_water_mm >= result["crop_water_need"]:
            recommendations.append(
                "জমিতে আগে থেকেই পর্যাপ্ত পানি আছে। অতিরিক্ত পানি জমে থাকলে ফসলের ক্ষতি হতে পারে।"
            )

        soil_label = bangla_value_label(data["soil_type"])

        if soil_label.startswith("বেলে"):
            recommendations.append(
                "বেলে মাটিতে পানি দ্রুত নিচে চলে যায়। প্রয়োজন হলে একবারে বেশি পানি না দিয়ে ভাগ করে সেচ দিন।"
            )

        if soil_label.startswith("এঁটেল"):
            recommendations.append(
                "এঁটেল মাটি পানি বেশি সময় ধরে রাখে। সেচ দেওয়ার আগে জমিতে পানি জমে আছে কিনা পরীক্ষা করুন।"
            )

        if "ড্রিপ" in str(data["irrigation_method"]):
            recommendations.append(
                "ড্রিপ সেচ পানি সাশ্রয়ে কার্যকর এবং নিয়ন্ত্রিতভাবে পানি সরবরাহ করতে সাহায্য করে।"
            )

        for rec in recommendations:
            st.write(rec)

        # ====================================================
        # পানির ভারসাম্যের চার্ট
        # ====================================================

        chart_df = pd.DataFrame(
            {
                "বিভাগ": [
                    "ফসলের চাহিদা",
                    "জমিতে থাকা পানি",
                    "কার্যকর বৃষ্টি",
                    "প্রয়োজনীয় সেচ",
                ],
                "পানির পরিমাণ": [
                    result["crop_water_need"],
                    data["existing_water"],
                    result["effective_rain"],
                    result["gross_water_mm"],
                ],
            }
        )

        chart_df["বাংলা মান"] = chart_df["পানির পরিমাণ"].apply(
            lambda x: bn_num(x, 2)
        )

        fig = px.bar(
            chart_df,
            x="বিভাগ",
            y="পানির পরিমাণ",
            title="কৃষি পানির ভারসাম্য",
            text="বাংলা মান",
        )

        fig.update_traces(texttemplate="%{text}", textposition="outside")

        fig.update_layout(
            xaxis_title="",
            yaxis_title="পানির পরিমাণ (মিমি)",
        )

        st.plotly_chart(
            fig,
            width="stretch",
        )
