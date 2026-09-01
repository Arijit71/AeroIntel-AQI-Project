import pandas as pd
import joblib


def predict_aqi(input_data):
    """
    Predict AQI for new pollutant values.
    """

    # Load saved model
    model = joblib.load("models/random_forest_model.pkl")

    # Load imputer
    imputer = joblib.load("models/imputer.pkl")

    # Load scaler
    scaler = joblib.load("models/scaler.pkl")

    # Feature names in the exact training order
    features = [
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

    # Convert input dictionary into DataFrame
    input_df = pd.DataFrame(
        [input_data],
        columns=features
    )

    # Apply same preprocessing
    input_imputed = imputer.transform(input_df)

    input_scaled = scaler.transform(input_imputed)

    # Predict AQI
    prediction = model.predict(input_scaled)

    return prediction[0]