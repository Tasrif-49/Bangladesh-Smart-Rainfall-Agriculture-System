import streamlit as st
import plotly.io as pio


# ============================================================
# IMPORT SETTINGS
# ============================================================

from config.settings import (
    INDIGO,
    SLATE,
    TEAL,
    AMBER,
    GREEN,
    INK,
    LINE
)


# ============================================================
# IMPORT SERVICES
# ============================================================

from services.data_loader import (
    load_model,
    load_dataset,
    validate_dataset,
    prepare_dataset,
    get_model_history_days
)


# ============================================================
# IMPORT VIEWS
# ============================================================

from views.home import show_home
from views.prediction import show_prediction
from views.agriculture import show_agriculture
from views.data_page import show_data_page
from views.analytics import show_analytics
from views.about import show_about


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Bangladesh Rainfall & Agriculture System",
    page_icon="🌧️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PLOTLY THEME
# ============================================================

pio.templates["monsoon"] = pio.templates["plotly_white"]

pio.templates["monsoon"].layout.colorway = [
    TEAL,
    INDIGO,
    AMBER,
    SLATE,
    GREEN,
    "#6FA8C4"
]

pio.templates["monsoon"].layout.font = dict(
    family="Inter, sans-serif",
    color=INK,
    size=13
)

pio.templates["monsoon"].layout.title.font = dict(
    family="Space Grotesk, sans-serif",
    size=16,
    color=INDIGO
)

pio.templates["monsoon"].layout.paper_bgcolor = "rgba(0,0,0,0)"
pio.templates["monsoon"].layout.plot_bgcolor = "rgba(0,0,0,0)"

pio.templates["monsoon"].layout.xaxis.gridcolor = LINE
pio.templates["monsoon"].layout.yaxis.gridcolor = LINE

pio.templates.default = "monsoon"


# ============================================================
# CSS - PROFESSIONAL UI
# ============================================================

st.markdown(
    """
<style>

/* =========================================================
   GOOGLE FONTS
========================================================= */

@import url(
'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Noto+Sans+Bengali:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap'
);


/* =========================================================
   ROOT COLORS
========================================================= */

:root {
    --bg: #F4F7FA;
    --card: #FFFFFF;
    --ink: #102A43;
    --text: #102A43;
    --muted: #5C6B78;
    --indigo: #0B1D33;
    --slate: #1B4965;
    --teal: #168F87;
    --teal-light: #E8F7F5;
    --green: #2E8B57;
    --amber: #E8873A;
    --line: #D5DEE7;
}


/* =========================================================
   GLOBAL
========================================================= */

html,
body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {

    background-color: var(--bg) !important;
    color: var(--text) !important;

    font-family:
        'Inter',
        'Noto Sans Bengali',
        sans-serif !important;
}


.stApp {
    background-color: var(--bg) !important;
    color: var(--text) !important;
}


/* =========================================================
   MAIN TEXT
========================================================= */

[data-testid="stMain"] p,
[data-testid="stMain"] li {
    color: var(--text) !important;
}

[data-testid="stMain"] .stMarkdown,
[data-testid="stMain"] .stMarkdown p,
[data-testid="stMain"] .stMarkdown li {
    color: var(--text) !important;
}


/* =========================================================
   HEADINGS
========================================================= */

[data-testid="stMain"] h1,
[data-testid="stMain"] h2,
[data-testid="stMain"] h3,
[data-testid="stMain"] h4 {

    color: var(--indigo) !important;

    font-family:
        'Space Grotesk',
        'Noto Sans Bengali',
        sans-serif !important;

    font-weight: 700 !important;
}


/* =========================================================
   MAIN CONTAINER
========================================================= */

.block-container {

    max-width: 1380px !important;

    padding-top: 1.6rem !important;
    padding-bottom: 2rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}


/* =========================================================
   HOME HERO
========================================================= */

.hero {

    position: relative;
    overflow: hidden;

    padding: 2.6rem;

    border-radius: 22px;

    background:
        linear-gradient(
            135deg,
            #0B1D33 0%,
            #123A56 52%,
            #168F87 100%
        ) !important;

    box-shadow:
        0 12px 32px
        rgba(11, 29, 51, 0.16);

    margin-bottom: 1.8rem;
}


.hero h1 {

    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;

    font-size: 2rem !important;
    line-height: 1.35 !important;

    margin-bottom: 0.7rem !important;
}


.hero p {

    color: #E3F1F5 !important;
    -webkit-text-fill-color: #E3F1F5 !important;

    font-size: 1.05rem !important;
    line-height: 1.7 !important;

    margin-bottom: 0 !important;
}


/* =========================================================
   HERO STATS
========================================================= */

.hero-stats {

    display: flex;
    gap: 2.5rem;
    flex-wrap: wrap;

    margin-top: 1.8rem;
}


.hero-stat {

    border-left:
        4px solid #55D6C2;

    padding-left: 0.9rem;
}


.hero-num {

    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;

    font-size: 1.55rem !important;
    font-weight: 700 !important;

    line-height: 1.3 !important;
}


.hero-label {

    color: #CDE5EC !important;
    -webkit-text-fill-color: #CDE5EC !important;

    font-size: 0.88rem !important;

    margin-top: 0.25rem !important;
}


/* =========================================================
   SECTION TITLE
========================================================= */

.section-title {

    font-size: 1.25rem;
    font-weight: 700;

    color: var(--indigo) !important;

    margin-top: 1.8rem;
    margin-bottom: 1rem;

    padding-left: 0.8rem;

    border-left:
        4px solid var(--teal);
}


/* =========================================================
   STANDARD CARD
========================================================= */

.card {

    background: #FFFFFF !important;
    color: var(--text) !important;

    border:
        1px solid var(--line);

    border-radius: 16px;

    padding: 1.3rem;

    margin-bottom: 1rem;

    box-shadow:
        0 4px 15px
        rgba(15, 36, 54, 0.04);
}


.card p,
.card span {
    color: var(--text) !important;
}


/* =========================================================
   AGRICULTURE CARD
========================================================= */

.agri-card {

    background:
        linear-gradient(
            135deg,
            #F1FAF5,
            #FFFFFF
        ) !important;

    color: var(--text) !important;

    border:
        1px solid #B8DEC7;

    border-left:
        6px solid var(--green);

    border-radius: 16px;

    padding: 1.4rem;

    margin-bottom: 1.2rem;
}


.agri-card h1,
.agri-card h2,
.agri-card h3,
.agri-card h4 {
    color: #176B3A !important;
}


.agri-card p {
    color: var(--text) !important;
    line-height: 1.7;
}


/* =========================================================
   RESULT CARD
========================================================= */

.result-card {

    background:
        linear-gradient(
            135deg,
            #EAF8F0,
            #FFFFFF
        ) !important;

    color: var(--text) !important;

    border:
        1px solid #A8D9BB;

    border-radius: 18px;

    padding: 1.5rem;

    margin-bottom: 1rem;
}


.result-card h1,
.result-card h2,
.result-card h3 {
    color: #176B3A !important;
}


.result-card p {
    color: #176B3A !important;
}


/* =========================================================
   INPUT LABELS
========================================================= */

[data-testid="stMain"] label {

    color: #102A43 !important;

    font-weight: 600 !important;

    font-size: 0.95rem !important;

    opacity: 1 !important;
}


/* =========================================================
   GENERAL INPUT
   IMPORTANT:
   Do NOT force text-fill-color here.
   This avoids interfering with Streamlit date inputs.
========================================================= */

[data-testid="stMain"] input:not([type="date"]) {

    background-color: #FFFFFF !important;

    color: #102A43 !important;

    caret-color: #102A43 !important;

    border-color: #BFCBD5 !important;

    opacity: 1 !important;
}


/* =========================================================
   GENERAL BASE INPUT
========================================================= */

[data-baseweb="input"] {
    background-color: #FFFFFF !important;
}


/* =========================================================
   NUMBER INPUT
========================================================= */

[data-testid="stNumberInput"] input {

    color: #102A43 !important;

    background-color: #FFFFFF !important;

    opacity: 1 !important;
}


/* =========================================================
   TEXT AREA
========================================================= */

[data-testid="stMain"] textarea {

    background-color: #FFFFFF !important;

    color: #102A43 !important;
}


/* =========================================================
   SELECTBOX
========================================================= */

[data-testid="stSelectbox"] {
    opacity: 1 !important;
}


[data-testid="stSelectbox"] label,
[data-testid="stSelectbox"] label p,
[data-testid="stSelectbox"] label span {

    color: #102A43 !important;

    font-weight: 600 !important;

    opacity: 1 !important;
}


[data-testid="stMain"] [data-baseweb="select"],
[data-testid="stMain"] [data-baseweb="select"] > div {

    background-color: #FFFFFF !important;

    color: #102A43 !important;

    border-color: #BFCBD5 !important;

    opacity: 1 !important;
}


[data-testid="stMain"] [data-baseweb="select"] div,
[data-testid="stMain"] [data-baseweb="select"] span,
[data-testid="stMain"] [data-baseweb="select"] p,
[data-testid="stMain"] [data-baseweb="select"] input {

    color: #102A43 !important;

    opacity: 1 !important;
}


[data-testid="stMain"] [data-baseweb="select"] input {

    background-color: transparent !important;

    caret-color: #102A43 !important;
}


[data-testid="stMain"] [data-baseweb="select"] input::placeholder {

    color: #52616B !important;

    opacity: 1 !important;
}


[data-testid="stMain"] [data-baseweb="select"] svg {

    color: #102A43 !important;

    fill: currentColor !important;

    stroke: currentColor !important;

    opacity: 1 !important;
}


[data-testid="stMain"] [data-baseweb="select"]:focus-within > div {

    background-color: #FFFFFF !important;

    border-color: #168F87 !important;
}


/* =========================================================
   DROPDOWN MENU
========================================================= */

[data-baseweb="popover"],
[data-baseweb="menu"],
[role="listbox"] {

    background-color: #FFFFFF !important;

    color: #102A43 !important;
}


[role="option"] {

    background-color: #FFFFFF !important;

    color: #102A43 !important;

    opacity: 1 !important;
}


[role="option"]:hover,
[role="option"][aria-selected="true"] {

    background-color: #E8F7F5 !important;

    color: #102A43 !important;
}


/* =========================================================
   DATE INPUTS
   SAFE / MINIMAL CSS
   IMPORTANT:
   Do not style internal date segments.
========================================================= */

.st-key-prediction_date,
.st-key-historical_date_range {

    width: 100% !important;
}


/* Date box background only */

.st-key-prediction_date [data-testid="stDateInput"] > div,
.st-key-historical_date_range [data-testid="stDateInput"] > div {

    background-color: #FFFFFF !important;

    border-radius: 8px !important;
}


/* Keep date text visible */

.st-key-prediction_date [data-testid="stDateInput"] input,
.st-key-historical_date_range [data-testid="stDateInput"] input {

    background-color: #FFFFFF !important;

    color: #102A43 !important;

    opacity: 1 !important;
}


/* Calendar button */

.st-key-prediction_date [data-testid="stDateInput"] button,
.st-key-historical_date_range [data-testid="stDateInput"] button {

    background-color: #FFFFFF !important;

    color: #102A43 !important;

    border: none !important;
}


/* Calendar icon */

.st-key-prediction_date [data-testid="stDateInput"] button svg,
.st-key-historical_date_range [data-testid="stDateInput"] button svg {

    color: #102A43 !important;

    opacity: 1 !important;
}


/* =========================================================
   RADIO
========================================================= */

[data-testid="stRadio"] label {
    color: #102A43 !important;
    font-weight: 500 !important;
}


[data-testid="stRadio"] p {
    color: #102A43 !important;
}


/* =========================================================
   SLIDER
========================================================= */

[data-testid="stSlider"] {
    color: var(--indigo) !important;
}


/* =========================================================
   NORMAL BUTTON
========================================================= */

.stButton > button {

    min-height: 44px !important;

    border-radius: 10px !important;

    font-weight: 600 !important;

    border:
        1px solid var(--teal) !important;

    color:
        var(--teal) !important;

    background:
        #FFFFFF !important;

    transition:
        all 0.2s ease !important;
}


.stButton > button:hover {

    background:
        #E8F7F5 !important;

    border-color:
        #168F87 !important;

    transform:
        translateY(-1px);
}


/* =========================================================
   PRIMARY BUTTON
========================================================= */

.stButton > button[kind="primary"] {

    background:
        linear-gradient(
            135deg,
            #168F87,
            #1F9E92
        ) !important;

    color:
        #FFFFFF !important;

    border-color:
        #168F87 !important;

    box-shadow:
        0 4px 12px
        rgba(22, 143, 135, 0.18);
}


.stButton > button[kind="primary"] p,
.stButton > button[kind="primary"] span {

    color:
        #FFFFFF !important;
}


/* =========================================================
   FORM SUBMIT BUTTON
========================================================= */

[data-testid="stFormSubmitButton"] button {

    min-height: 46px !important;

    background:
        linear-gradient(
            135deg,
            #168F87,
            #1F9E92
        ) !important;

    color:
        #FFFFFF !important;

    border:
        none !important;

    border-radius:
        10px !important;

    font-weight:
        700 !important;

    box-shadow:
        0 4px 14px
        rgba(22, 143, 135, 0.20) !important;

    transition:
        all 0.2s ease !important;
}


[data-testid="stFormSubmitButton"] button:hover {

    transform:
        translateY(-1px);

    box-shadow:
        0 7px 18px
        rgba(22, 143, 135, 0.28) !important;
}


[data-testid="stFormSubmitButton"] button p,
[data-testid="stFormSubmitButton"] button span {

    color:
        #FFFFFF !important;
}


/* =========================================================
   METRICS
========================================================= */

div[data-testid="stMetric"] {

    background:
        #FFFFFF !important;

    border:
        1px solid var(--line) !important;

    border-radius:
        14px !important;

    padding:
        1rem !important;

    box-shadow:
        0 3px 12px
        rgba(15, 36, 54, 0.04);
}


[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] * {

    color:
        var(--muted) !important;
}


[data-testid="stMetricValue"],
[data-testid="stMetricValue"] * {

    color:
        var(--indigo) !important;

    font-weight:
        700 !important;
}


/* =========================================================
   DATAFRAME
========================================================= */

[data-testid="stDataFrame"] {

    background:
        #FFFFFF !important;

    border:
        1px solid var(--line) !important;

    border-radius:
        12px !important;

    overflow:
        hidden !important;
}


/* =========================================================
   EXPANDER
========================================================= */

[data-testid="stExpander"] {

    background:
        #FFFFFF !important;

    border:
        1px solid var(--line) !important;

    border-radius:
        12px !important;

    overflow:
        hidden !important;
}


[data-testid="stExpander"] p,
[data-testid="stExpander"] span {

    color:
        #102A43 !important;
}


/* =========================================================
   ALERTS
========================================================= */

[data-testid="stAlert"] {
    border-radius: 12px !important;
}


/* =========================================================
   DIVIDER
========================================================= */

hr {
    border-color: var(--line) !important;
}


/* =========================================================
   SIDEBAR
========================================================= */

[data-testid="stSidebar"] {

    background:
        linear-gradient(
            180deg,
            #0B1D33 0%,
            #132D42 100%
        ) !important;
}


[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label {

    color:
        #F2F7FA !important;
}


[data-testid="stSidebar"]
[data-testid="stRadio"] label {

    color:
        #FFFFFF !important;
}


[data-testid="stSidebar"]
[data-testid="stRadio"] p {

    color:
        #FFFFFF !important;
}


[data-testid="stSidebar"] button {
    color:
        #FFFFFF !important;
}


[data-testid="stSidebar"] input {

    color:
        #102A43 !important;
}


/* =========================================================
   FOOTER
========================================================= */

.footer {

    text-align:
        center;

    color:
        #52616B !important;

    padding:
        2rem 0 1rem;

    line-height:
        1.8;
}


.footer b {
    color:
        #0B1D33 !important;
}


/* =========================================================
   PLOTLY
========================================================= */

.js-plotly-plot {
    background:
        transparent !important;
}


/* =========================================================
   HIDE STREAMLIT DEFAULT
========================================================= */

#MainMenu {
    visibility:
        hidden;
}


footer {
    visibility:
        hidden;
}


/* =========================================================
   MOBILE
========================================================= */

@media (max-width: 768px) {

    .block-container {

        padding-left:
            1rem !important;

        padding-right:
            1rem !important;

        padding-top:
            1rem !important;
    }


    .hero {

        padding:
            1.5rem !important;

        border-radius:
            18px !important;
    }


    .hero h1 {

        font-size:
            1.45rem !important;
    }


    .hero p {

        font-size:
            0.95rem !important;
    }


    .hero-stats {

        gap:
            1.2rem !important;
    }


    .hero-num {

        font-size:
            1.3rem !important;
    }

}

</style>
""",
    unsafe_allow_html=True
)


# ============================================================
# LOAD DATA
# ============================================================

try:

    package, MODEL_FILE = load_model()

    df, CSV_FILE = load_dataset()

    validate_dataset(df)

    df = prepare_dataset(df)

    model = package["model"]

    feature_columns = package["feature_columns"]

    train_medians = package["train_medians"]

    HISTORY_DAYS = get_model_history_days(
        feature_columns
    )


except Exception as e:

    st.error(
        "❌ System file loading failed"
    )

    st.exception(e)

    st.stop()


# ============================================================
# PAGES
# ============================================================

PAGES = [

    "🏠 Home",
    "🔮 Rain Prediction",
    "🌱 Agriculture (কৃষি সেচ ব্যবস্থা)",
    "📂 Historical Data",
    "📊 Analytics",
    "ℹ️ About"

]


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = PAGES[0]


if st.session_state.page not in PAGES:
    st.session_state.page = PAGES[0]


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.markdown(
    """
    <div style="
    font-family:Space Grotesk;
    font-weight:700;
    font-size:1.25rem;
    color:#fff;
    padding:.2rem 0 1rem 0
    ">

    🌧️ Smart Rain & Agriculture

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# NAVIGATION
# ============================================================

page_index = PAGES.index(
    st.session_state.page
)


selected_page = st.sidebar.radio(
    "Navigation",
    PAGES,
    index=page_index,
    label_visibility="collapsed"
)


# ============================================================
# UPDATE PAGE
# ============================================================

if selected_page != st.session_state.page:

    st.session_state.page = selected_page

    st.rerun()


# ============================================================
# ROUTING
# ============================================================

page = st.session_state.page


if page == "🏠 Home":

    show_home(df)


elif page == "🔮 Rain Prediction":

    show_prediction(
        df=df,
        model=model,
        feature_columns=feature_columns,
        train_medians=train_medians,
        history_days=HISTORY_DAYS
    )


elif page == "🌱 Agriculture":

    show_agriculture()


elif page == "📂 Historical Data":

    show_data_page(df)


elif page == "📊 Analytics":

    show_analytics(df)


elif page == "ℹ️ About":

    show_about()


# ============================================================
# QUICK NAVIGATION
# ============================================================

st.divider()

cols = st.columns(4)

quick_pages = [

    (
        "🏠 Home",
        "🏠 Home"
    ),

    (
        "🔮 Prediction",
        "🔮 Rain Prediction"
    ),

    (
        "🌱 Agriculture",
        "🌱 Agriculture"
    ),

    (
        "📊 Analytics",
        "📊 Analytics"
    )

]


for col, (button_text, target_page) in zip(
    cols,
    quick_pages
):

    if col.button(
        button_text,
        width="stretch",
        key=f"quick_nav_{target_page}"
    ):

        st.session_state.page = target_page

        st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class='footer'>

    <b>
    🌧️ Bangladesh Smart Rainfall & Agriculture System
    </b>

    <br>

    🌱 Rain Prediction • Smart Irrigation • Agriculture

    <br>

    Made by

    <b>
    Shams, Tasrif & Jishan
    </b>

    </div>
    """,
    unsafe_allow_html=True
)