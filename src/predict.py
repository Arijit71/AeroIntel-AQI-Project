import os
from pathlib import Path
import pandas as pd
import joblib

# Global caches for trained artifacts
_CACHED_MODEL = None
_CACHED_IMPUTER = None
_CACHED_SCALER = None

FEATURE_COLUMNS = [
    "PM2.5",
    "PM10",
    "NO",
    "NO2",
    "NOx",
    "NH3",
    "CO",
    "SO2",
    "O3",
    "Benzene",
    "Toluene"
]

# Standard Indian CPCB AQI Breakpoints: (C_low, C_high, I_low, I_high)
BREAKPOINTS = {
    "PM2.5": [
        (0, 30, 0, 50),
        (31, 60, 51, 100),
        (61, 90, 101, 200),
        (91, 120, 201, 300),
        (121, 250, 301, 400),
        (251, 500, 401, 500)
    ],
    "PM10": [
        (0, 50, 0, 50),
        (51, 100, 51, 100),
        (101, 250, 101, 200),
        (251, 350, 201, 300),
        (351, 430, 301, 400),
        (431, 600, 401, 500)
    ],
    "NO2": [
        (0, 40, 0, 50),
        (41, 80, 51, 100),
        (81, 180, 101, 200),
        (181, 280, 201, 300),
        (281, 400, 301, 400),
        (401, 600, 401, 500)
    ],
    "NH3": [
        (0, 200, 0, 50),
        (201, 400, 51, 100),
        (401, 800, 101, 200),
        (801, 1200, 201, 300),
        (1201, 1800, 301, 400),
        (1801, 2500, 401, 500)
    ],
    "SO2": [
        (0, 40, 0, 50),
        (41, 80, 51, 100),
        (81, 380, 101, 200),
        (381, 800, 201, 300),
        (801, 1600, 301, 400),
        (1601, 2000, 401, 500)
    ],
    "CO": [
        (0, 1.0, 0, 50),
        (1.1, 2.0, 51, 100),
        (2.1, 10.0, 101, 200),
        (10.1, 17.0, 201, 300),
        (17.1, 34.0, 301, 400),
        (34.1, 50.0, 401, 500)
    ],
    "O3": [
        (0, 50, 0, 50),
        (51, 100, 51, 100),
        (101, 168, 101, 200),
        (169, 208, 201, 300),
        (209, 748, 301, 400),
        (749, 1000, 401, 500)
    ]
}


def compute_sub_index(pollutant, concentration):
    """
    Computes Indian standard sub-index for an individual pollutant.
    """
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
            sub = ((i_high - i_low) / (c_high - c_low)) * (val - c_low) + i_low
            return round(sub, 1)

    if val > bp_list[-1][1]:
        return 500.0

    return None


def calculate_sub_indices(input_data):
    """
    Calculate sub-indices for all supported pollutants.
    """
    sub_indices = {}
    for pol in BREAKPOINTS:
        if pol in input_data and input_data[pol] is not None:
            sub = compute_sub_index(pol, input_data[pol])
            if sub is not None:
                sub_indices[pol] = sub
    return sub_indices


def get_aqi_category(aqi):
    """
    Categorize AQI based on National Air Quality Index (NAQI) standards.
    """
    if aqi <= 50:
        return {
            "name": "Good",
            "class": "good",
            "color": "#10B981",
            "textColor": "#064E3B",
            "summary": "Minimal Health Impact",
            "health_advisory": "Air quality is satisfactory, and air pollution poses little or no risk.",
            "sensitive_advisory": "Safe for everyone to engage in normal outdoor activities."
        }
    elif aqi <= 100:
        return {
            "name": "Satisfactory",
            "class": "satisfactory",
            "color": "#84CC16",
            "textColor": "#365314",
            "summary": "Minor Breathing Discomfort to Sensitive People",
            "health_advisory": "Air quality is acceptable; however, unusually sensitive individuals may experience minor symptoms.",
            "sensitive_advisory": "Sensitive individuals should monitor physical comfort during prolonged outdoor exertion."
        }
    elif aqi <= 200:
        return {
            "name": "Moderate",
            "class": "moderate",
            "color": "#F59E0B",
            "textColor": "#78350F",
            "summary": "Breathing Discomfort to People with Lungs/Heart Diseases",
            "health_advisory": "May cause breathing discomfort to children, the elderly, and people with existing respiratory conditions.",
            "sensitive_advisory": "Reduce strenuous outdoor activities if you experience coughing or shortness of breath."
        }
    elif aqi <= 300:
        return {
            "name": "Poor",
            "class": "poor",
            "color": "#F97316",
            "textColor": "#7C2D12",
            "summary": "Breathing Discomfort to Most People on Prolonged Exposure",
            "health_advisory": "Prolonged exposure can cause breathing discomfort to most individuals and serious impacts on sensitive groups.",
            "sensitive_advisory": "Wear an N95 mask outdoors, keep windows closed, and limit physical exertion outside."
        }
    elif aqi <= 400:
        return {
            "name": "Very Poor",
            "class": "very-poor",
            "color": "#EF4444",
            "textColor": "#7F1D1D",
            "summary": "Respiratory Illness on Prolonged Exposure",
            "health_advisory": "Triggers significant health alerts. Vulnerable individuals may develop acute respiratory distress.",
            "sensitive_advisory": "Avoid all outdoor activity. Use indoor air purifiers and wear protective respirators."
        }
    else:
        return {
            "name": "Severe",
            "class": "severe",
            "color": "#881337",
            "textColor": "#4C0519",
            "summary": "Severe Health Impact Even on Healthy People",
            "health_advisory": "Emergency health conditions. High risk of adverse respiratory and cardiovascular effects for everyone.",
            "sensitive_advisory": "Remain strictly indoors. Keep ventilation closed and use HEPA air purifiers."
        }


def load_model_artifacts():
    """
    Load model and preprocessing objects from disk with in-memory caching.
    """
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
            print(f"Warning: Failed to load serialized artifacts ({e}).")

    return None, None, None


def sanitize_input(input_data):
    """
    Sanitizes pollutant input values, clamping negative numbers and ensuring floats.
    """
    clean = {}
    for col in FEATURE_COLUMNS:
        val = input_data.get(col, 0.0)
        try:
            val_float = float(val)
            clean[col] = max(0.0, val_float)
        except (ValueError, TypeError):
            clean[col] = 0.0
    return clean


def predict_aqi(input_data):
    """
    Predict AQI for new pollutant values.
    Uses trained Random Forest if artifacts exist; otherwise computes CPCB sub-index standard.
    """
    model, imputer, scaler = load_model_artifacts()
    safe_data = sanitize_input(input_data)

    if model is not None and imputer is not None and scaler is not None:
        input_df = pd.DataFrame([safe_data], columns=FEATURE_COLUMNS)
        input_imputed = imputer.transform(input_df)
        input_scaled = scaler.transform(input_imputed)
        prediction = model.predict(input_scaled)[0]
        return max(0.0, min(500.0, float(prediction)))

    sub_indices = calculate_sub_indices(safe_data)
    if sub_indices:
        predicted = max(sub_indices.values())
        return float(predicted)

    return 50.0


def predict_aqi_full_report(input_data):
    """
    Generate comprehensive AQI report including score, category, dominant pollutant,
    sub-indices, and advisory guidance.
    """
    model, _, _ = load_model_artifacts()
    is_ml_model = model is not None

    aqi_score = predict_aqi(input_data)
    aqi_score = round(aqi_score, 1)

    sub_indices = calculate_sub_indices(input_data)
    dominant_pollutant = "PM2.5"
    if sub_indices:
        dominant_pollutant = max(sub_indices.items(), key=lambda x: x[1])[0]

    category_info = get_aqi_category(aqi_score)

    return {
        "aqi": aqi_score,
        "is_ml_model": is_ml_model,
        "category": category_info["name"],
        "category_class": category_info["class"],
        "category_color": category_info["color"],
        "category_text_color": category_info["textColor"],
        "summary": category_info["summary"],
        "health_advisory": category_info["health_advisory"],
        "sensitive_advisory": category_info["sensitive_advisory"],
        "dominant_pollutant": dominant_pollutant,
        "sub_indices": sub_indices
    }