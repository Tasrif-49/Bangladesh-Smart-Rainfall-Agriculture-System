# ============================================================
# CROPS
# ============================================================

CROPS = {

    "ধান (Rice)": {
        "name": "ধান (Rice)",
        "water_mm": 7.0,
        "min_mm": 4.0,
        "max_mm": 10.0,
        "description": "ধান সাধারণত বেশি পানি প্রয়োজন করে।",
        "stage_factor": {

            "চারা (Seedling)": 0.80,
            "বৃদ্ধি (Vegetative)": 1.00,
            "ফুল (Flowering)": 1.20,
            "দানার বৃদ্ধি (Grain Filling)": 1.10,
            "পাকা (Maturity)": 0.60

        }
    },


    "গম (Wheat)": {
        "name": "গম (Wheat)",
        "water_mm": 5.0,
        "min_mm": 3.0,
        "max_mm": 7.0,
        "description": "গমের জন্য মাঝারি পরিমাণ পানি প্রয়োজন।",
        "stage_factor": {

            "চারা (Seedling)": 0.70,
            "বৃদ্ধি (Vegetative)": 1.00,
            "ফুল (Flowering)": 1.20,
            "দানার বৃদ্ধি (Grain Filling)": 1.10,
            "পাকা (Maturity)": 0.50

        }
    },


    "ভুট্টা (Maize)": {
        "name": "ভুট্টা (Maize)",
        "water_mm": 6.0,
        "min_mm": 3.0,
        "max_mm": 8.0,
        "description": "ফুল ও দানা গঠনের সময়ে ভুট্টার বেশি পানি প্রয়োজন।",
        "stage_factor": {

            "চারা (Seedling)": 0.70,
            "বৃদ্ধি (Vegetative)": 1.00,
            "ফুল (Flowering)": 1.30,
            "দানার বৃদ্ধি (Grain Filling)": 1.20,
            "পাকা (Maturity)": 0.60

        }
    },


    "আলু (Potato)": {
        "name": "আলু (Potato)",
        "water_mm": 5.0,
        "min_mm": 3.0,
        "max_mm": 7.0,
        "description": "আলুর জমিতে অতিরিক্ত পানি জমে থাকা ক্ষতিকর।",
        "stage_factor": {

            "চারা (Seedling)": 0.70,
            "বৃদ্ধি (Vegetative)": 1.00,
            "ফুল (Flowering)": 1.20,
            "দানার বৃদ্ধি (Grain Filling)": 1.00,
            "পাকা (Maturity)": 0.60

        }
    },


    "টমেটো (Tomato)": {
        "name": "টমেটো (Tomato)",
        "water_mm": 5.5,
        "min_mm": 3.0,
        "max_mm": 7.0,
        "description": "টমেটোর জন্য নিয়মিত কিন্তু নিয়ন্ত্রিত সেচ প্রয়োজন।",
        "stage_factor": {

            "চারা (Seedling)": 0.70,
            "বৃদ্ধি (Vegetative)": 1.00,
            "ফুল (Flowering)": 1.20,
            "দানার বৃদ্ধি (Grain Filling)": 1.20,
            "পাকা (Maturity)": 0.80

        }
    },


    "পেঁয়াজ (Onion)": {
        "name": "পেঁয়াজ (Onion)",
        "water_mm": 4.0,
        "min_mm": 2.0,
        "max_mm": 6.0,
        "description": "অতিরিক্ত পানি পেঁয়াজের জন্য ক্ষতিকর হতে পারে।",
        "stage_factor": {

            "চারা (Seedling)": 0.70,
            "বৃদ্ধি (Vegetative)": 1.00,
            "ফুল (Flowering)": 1.00,
            "দানার বৃদ্ধি (Grain Filling)": 0.90,
            "পাকা (Maturity)": 0.50

        }
    },


    "সবজি (Vegetables)": {
        "name": "সবজি (Vegetables)",
        "water_mm": 5.0,
        "min_mm": 3.0,
        "max_mm": 7.0,
        "description": "সাধারণ সবজির জন্য মাঝারি পরিমাণ পানি প্রয়োজন।",
        "stage_factor": {

            "চারা (Seedling)": 0.70,
            "বৃদ্ধি (Vegetative)": 1.00,
            "ফুল (Flowering)": 1.20,
            "দানার বৃদ্ধি (Grain Filling)": 1.00,
            "পাকা (Maturity)": 0.70

        }
    },


    "সরিষা (Mustard)": {
        "name": "সরিষা (Mustard)",
        "water_mm": 3.5,
        "min_mm": 2.0,
        "max_mm": 5.0,
        "description": "সরিষার জন্য তুলনামূলক কম পানি প্রয়োজন।",
        "stage_factor": {

            "চারা (Seedling)": 0.70,
            "বৃদ্ধি (Vegetative)": 1.00,
            "ফুল (Flowering)": 1.20,
            "দানার বৃদ্ধি (Grain Filling)": 1.00,
            "পাকা (Maturity)": 0.50

        }
    }

}


# ============================================================
# SOIL TYPES
# ============================================================

SOIL_TYPES = {

    "বেলে মাটি (Sandy Soil)": {
        "factor": 1.20,
        "description": "বেলে মাটিতে পানি দ্রুত নিচে চলে যায়, তাই বেশি সেচ লাগতে পারে।"
    },


    "দোআঁশ মাটি (Loamy Soil)": {
        "factor": 1.00,
        "description": "দোআঁশ মাটির পানি ধারণক্ষমতা মাঝারি এবং ভালো।"
    },


    "এঁটেল মাটি (Clay Soil)": {
        "factor": 0.85,
        "description": "এঁটেল মাটি পানি বেশি সময় ধরে রাখতে পারে।"
    }

}


# ============================================================
# WATER DEPTH CONVERSION
# ============================================================

WATER_DEPTH_OPTIONS = {

    "পানি নেই (No Water)": 0,

    "আধা আঙুল (Half Finger)": 8,

    "১ আঙুল (One Finger)": 15,

    "২ আঙুল (Two Fingers)": 30,

    "৩ আঙুল (Three Fingers)": 45,

    "৪ আঙুল (Four Fingers)": 60

}


# ============================================================
# AREA CONVERSION
# ============================================================

def convert_area_to_m2(land_area, area_unit):

    if area_unit == "শতক (Decimal)":
        return land_area * 40.4686

    elif area_unit == "একর (Acre)":
        return land_area * 4046.86

    elif area_unit == "হেক্টর (Hectare)":
        return land_area * 10000

    else:
        return land_area


# ============================================================
# WATER DEPTH TO MM
# ============================================================

def convert_water_depth_to_mm(
    water_measurement,
    custom_depth_cm=0.0
):

    if water_measurement == "নিজে পরিমাপ দিন (Custom Measurement)":

        return custom_depth_cm * 10

    return WATER_DEPTH_OPTIONS.get(
        water_measurement,
        0
    )


# ============================================================
# CALCULATE EXISTING WATER VOLUME
# ============================================================

def calculate_existing_water_volume(
    area_m2,
    water_depth_mm
):

    # 1 mm water over 1 square meter = 1 liter

    water_liters = (
        area_m2
        *
        water_depth_mm
    )

    water_m3 = (
        water_liters
        /
        1000
    )

    return {
        "water_liters": water_liters,
        "water_m3": water_m3
    }


# ============================================================
# CALCULATE IRRIGATION
# ============================================================

def calculate_irrigation(

    land_area,

    area_unit,

    crop_name,

    crop_stage,

    soil_type,

    existing_water_mm,

    predicted_rain_mm,

    et0_value,

    irrigation_efficiency

):


    crop = CROPS[crop_name]

    soil = SOIL_TYPES[soil_type]


    # ========================================================
    # AREA
    # ========================================================

    area_m2 = convert_area_to_m2(

        land_area,

        area_unit

    )


    # ========================================================
    # CROP WATER REQUIREMENT
    # ========================================================

    base_crop_water = crop["water_mm"]

    stage_factor = crop["stage_factor"][crop_stage]

    soil_factor = soil["factor"]


    crop_water_need = (

        base_crop_water

        *

        stage_factor

        *

        soil_factor

    )


    # ========================================================
    # ET0 FACTOR
    # ========================================================

    if et0_value > 0:

        et_factor = min(

            max(

                et0_value / 5,

                0.70

            ),

            1.40

        )

    else:

        et_factor = 1.0


    crop_water_need = (

        crop_water_need

        *

        et_factor

    )


    # ========================================================
    # EFFECTIVE RAINFALL
    # ========================================================

    if predicted_rain_mm <= 5:

        effective_rain = (

            predicted_rain_mm

            *

            0.90

        )


    elif predicted_rain_mm <= 20:

        effective_rain = (

            predicted_rain_mm

            *

            0.80

        )


    else:

        effective_rain = (

            predicted_rain_mm

            *

            0.65

        )


    # ========================================================
    # AVAILABLE WATER
    # ========================================================

    available_water = (

        existing_water_mm

        +

        effective_rain

    )


    # ========================================================
    # NET WATER REQUIREMENT
    # ========================================================

    net_water_needed = max(

        crop_water_need

        -

        available_water,

        0

    )


    # ========================================================
    # IRRIGATION EFFICIENCY
    # ========================================================

    efficiency = max(

        irrigation_efficiency / 100,

        0.10

    )


    gross_water_mm = (

        net_water_needed

        /

        efficiency

    )


    # ========================================================
    # WATER VOLUME
    # ========================================================

    # 1 mm water over 1 m² = 1 liter

    water_liters = (

        gross_water_mm

        *

        area_m2

    )


    water_m3 = (

        water_liters

        /

        1000

    )


    # ========================================================
    # STATUS
    # ========================================================

    if net_water_needed <= 0.5:

        status = "NO_IRRIGATION"

        status_bn = "আজ সেচ প্রয়োজন নেই"

        status_en = "No irrigation needed today"


    elif net_water_needed <= 3:

        status = "LOW"

        status_bn = "অল্প পরিমাণ সেচ দিন"

        status_en = "Light irrigation recommended"


    elif net_water_needed <= 7:

        status = "MEDIUM"

        status_bn = "মাঝারি পরিমাণ সেচ দিন"

        status_en = "Moderate irrigation recommended"


    else:

        status = "HIGH"

        status_bn = "বেশি পরিমাণ সেচ প্রয়োজন"

        status_en = "High irrigation requirement"


    return {

        "area_m2": area_m2,

        "crop_water_need": crop_water_need,

        "effective_rain": effective_rain,

        "existing_water": existing_water_mm,

        "available_water": available_water,

        "net_water_needed": net_water_needed,

        "gross_water_mm": gross_water_mm,

        "water_liters": water_liters,

        "water_m3": water_m3,

        "status": status,

        "status_bn": status_bn,

        "status_en": status_en

    }