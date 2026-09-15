# Bangladesh Smart Rainfall & Agriculture System

AI-based rainfall prediction and smart irrigation recommendation system.

## Features

- Rainfall Prediction
- CatBoost Model
- Weather API Integration
- Historical Weather Data
- Advanced Analytics
- Smart Agriculture
- Smart Irrigation Calculation

## Project Structure

```text
Bangladesh_Smart_Rainfall_Agriculture_System/

├── app.py
├── requirements.txt
├── README.md
│
├── config/
│   └── settings.py
│
├── services/
│   ├── data_loader.py
│   ├── weather_api.py
│   └── agriculture.py
│
├── views/
│   ├── home.py
│   ├── prediction.py
│   ├── agriculture.py
│   ├── data_page.py
│   ├── analytics.py
│   └── about.py
│
├── data/
│   └── bangladesh_weather_stations_FINAL(7).csv
│
├── models/
│   └── rainfall_model(4).pkl
│
└── assets/