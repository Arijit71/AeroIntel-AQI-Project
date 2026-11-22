from pathlib import Path
import numpy as np
import pandas as pd
import joblib

from src.source_identification import (
    identify_pollutants,
    analyze_pollution_sources
)

_CACHED_MODEL = None
_CACHED_IMPUTER = None
_CACHED_SCALER = None

FEATURE_COLUMNS = [
    "PM2.5", "PM10", "NO", "NO2", "NOx",
    "NH3", "CO", "SO2", "O3", "Benzene", "Toluene"
]

# Indian CPCB AQI Breakpoints: (C_low, C_high, I_low, I_high)
BREAKPOINTS = {
    "PM2.5": [
        (0.0, 30.0, 0, 50),
        (30.0, 60.0, 51, 100),
        (60.0, 90.0, 101, 200),
        (90.0, 120.0, 201, 300),
        (120.0, 250.0, 301, 400),
        (250.0, 500.0, 401, 500)
    ],
    "PM10": [
        (0.0, 50.0, 0, 50),
        (50.0, 100.0, 51, 100),
        (100.0, 250.0, 101, 200),
        (250.0, 350.0, 201, 300),
        (350.0, 430.0, 301, 400),
        (430.0, 600.0, 401, 500)
    ],
    "NO2": [
        (0.0, 40.0, 0, 50),
        (40.0, 80.0, 51, 100),
        (80.0, 180.0, 101, 200),
        (180.0, 280.0, 201, 300),
        (280.0, 400.0, 301, 400),
        (400.0, 600.0, 401, 500)
    ],
    "NH3": [
        (0.0, 200.0, 0, 50),
        (200.0, 400.0, 51, 100),
        (400.0, 800.0, 101, 200),
        (800.0, 1200.0, 201, 300),
        (1200.0, 1800.0, 301, 400),
        (1800.0, 2500.0, 401, 500)
    ],
    "SO2": [
        (0.0, 40.0, 0, 50),
        (40.0, 80.0, 51, 100),
        (80.0, 380.0, 101, 200),
        (380.0, 800.0, 201, 300),
        (800.0, 1600.0, 301, 400),
        (1600.0, 2000.0, 401, 500)
    ],
    "CO": [
        (0.0, 1.0, 0, 50),
        (1.0, 2.0, 51, 100),
        (2.0, 10.0, 101, 200),
        (10.0, 17.0, 201, 300),
        (17.0, 34.0, 301, 400),
        (34.0, 50.0, 401, 500)
    ],
    "O3": [
        (0.0, 50.0, 0, 50),
        (50.0, 100.0, 51, 100),
        (100.0, 168.0, 101, 200),
        (168.0, 208.0, 201, 300),
        (208.0, 748.0, 301, 400),
        (748.0, 1000.0, 401, 500)
    ]
}


def compute_sub_index(pollutant, concentration):
    if pollutant not in BREAKPOINTS or concentration is None:
        return None
    try:
        val = float(concentration)
    except (ValueError, TypeError):
        return None

    if val <= 0:
        return 0.0

    bp_list = BREAKPOINTS[pollutant]
    for c_low, c_high, i_low, i_high in bp_list:
        if c_low <= val <= c_high:
            if c_high == c_low:
                return float(i_low)
            return round(((i_high - i_low) / (c_high - c_low)) * (val - c_low) + i_low, 1)

    if val > bp_list[-1][1]:
        return 500.0
    return None


def calculate_sub_indices(input_data):
    sub_indices = {}
    for pol in BREAKPOINTS:
        if pol in input_data and input_data[pol] is not None:
            sub = compute_sub_index(pol, input_data[pol])
            if sub is not None:
                sub_indices[pol] = sub
    return sub_indices


def get_aqi_category(aqi):
    if aqi <= 50:
        return {
            "name": "Good", "class": "good", "color": "#10B981", "textColor": "#064E3B",
            "summary": "Minimal Health Impact",
            "health_advisory": "Air quality is satisfactory, posing little or no risk.",
            "sensitive_advisory": "Safe for everyone to engage in normal outdoor activities."
        }
    elif aqi <= 100:
        return {
            "name": "Satisfactory", "class": "satisfactory", "color": "#84CC16", "textColor": "#365314",
            "summary": "Minor Breathing Discomfort to Sensitive People",
            "health_advisory": "Air quality is acceptable; unusually sensitive individuals may experience minor symptoms.",
            "sensitive_advisory": "Sensitive individuals should monitor comfort during prolonged outdoor exertion."
        }
    elif aqi <= 200:
        return {
            "name": "Moderate", "class": "moderate", "color": "#F59E0B", "textColor": "#78350F",
            "summary": "Breathing Discomfort to People with Lungs/Heart Diseases",
            "health_advisory": "May cause breathing discomfort to children, elderly, and respiratory patients.",
            "sensitive_advisory": "Reduce strenuous outdoor activities if experiencing cough or throat irritation."
        }
    elif aqi <= 300:
        return {
            "name": "Poor", "class": "poor", "color": "#F97316", "textColor": "#7C2D12",
            "summary": "Breathing Discomfort to Most People on Prolonged Exposure",
            "health_advisory": "Prolonged exposure causes breathing discomfort and serious impacts on sensitive groups.",
            "sensitive_advisory": "Wear an N95 mask outdoors, keep windows closed, and limit outdoor exertion."
        }
    elif aqi <= 400:
        return {
            "name": "Very Poor", "class": "very-poor", "color": "#EF4444", "textColor": "#7F1D1D",
            "summary": "Respiratory Illness on Prolonged Exposure",
            "health_advisory": "Significant health alert. Vulnerable individuals may develop acute respiratory distress.",
            "sensitive_advisory": "Avoid outdoor activity. Use indoor air purifiers and wear protective respirators."
        }
    else:
        return {
            "name": "Severe", "class": "severe", "color": "#881337", "textColor": "#4C0519",
            "summary": "Severe Health Impact Even on Healthy People",
            "health_advisory": "Emergency health conditions. High risk of cardiovascular and respiratory effects.",
            "sensitive_advisory": "Remain strictly indoors with closed ventilation and HEPA filtration."
        }


def load_model_artifacts():
    global _CACHED_MODEL, _CACHED_IMPUTER, _CACHED_SCALER
    if _CACHED_MODEL is not None and _CACHED_IMPUTER is not None and _CACHED_SCALER is not None:
        return _CACHED_MODEL, _CACHED_IMPUTER, _CACHED_SCALER

    model_path = Path("models/random_forest_model.pkl")
    imputer_path = Path("models/imputer.pkl")
    scaler_path = Path("models/scaler.pkl")

    if model_path.exists() and imputer_path.exists() and scaler_path.exists():
        try:
            _CACHED_MODEL = joblib.load(model_path)
            _CACHED_IMPUTER = joblib.load(imputer_path)
            _CACHED_SCALER = joblib.load(scaler_path)
            return _CACHED_MODEL, _CACHED_IMPUTER, _CACHED_SCALER
        except Exception as e:
            print(f"Warning: Failed to load model artifacts ({e}).")

    return None, None, None


def sanitize_input(input_data):
    clean = {}
    for col in FEATURE_COLUMNS:
        val = input_data.get(col, None)
        if val is None or val == "":
            clean[col] = np.nan
        else:
            try:
                clean[col] = max(0.0, float(val))
            except (ValueError, TypeError):
                clean[col] = np.nan
    return clean


def predict_aqi(input_data):
    model, imputer, scaler = load_model_artifacts()
    safe_data = sanitize_input(input_data)
    sub_indices = calculate_sub_indices(safe_data)
    cpcb_max = max(sub_indices.values()) if sub_indices else 50.0

    if model is not None and imputer is not None and scaler is not None:
        input_df = pd.DataFrame([safe_data], columns=FEATURE_COLUMNS)
        input_imputed = imputer.transform(input_df)
        input_scaled = scaler.transform(input_imputed)
        prediction = model.predict(input_scaled)[0]
        rf_aqi = max(0.0, min(500.0, float(prediction)))
        final_aqi = max(rf_aqi, cpcb_max) if cpcb_max > 100 else rf_aqi
        return round(float(final_aqi), 1)

    return round(float(cpcb_max), 1)


def predict_aqi_full_report(input_data):
    model, _, _ = load_model_artifacts()
    aqi_score = predict_aqi(input_data)
    sub_indices = calculate_sub_indices(input_data)

    pollutant_id = identify_pollutants(input_data, sub_indices)
    source_analysis = analyze_pollution_sources(input_data)

    dominant_pollutant = "PM2.5"
    if pollutant_id.get("primary_driver"):
        dominant_pollutant = pollutant_id["primary_driver"]["key"]
    elif sub_indices:
        dominant_pollutant = max(sub_indices.items(), key=lambda x: x[1])[0]

    category_info = get_aqi_category(aqi_score)

    return {
        "aqi": aqi_score,
        "is_ml_model": (model is not None),
        "category": category_info["name"],
        "category_class": category_info["class"],
        "category_color": category_info["color"],
        "category_text_color": category_info["textColor"],
        "summary": category_info["summary"],
        "health_advisory": category_info["health_advisory"],
        "sensitive_advisory": category_info["sensitive_advisory"],
        "dominant_pollutant": dominant_pollutant,
        "sub_indices": sub_indices,
        "pollutant_identification": pollutant_id,
        "source_attribution": source_analysis
    }
