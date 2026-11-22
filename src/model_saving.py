import joblib
import os


def save_model(model, imputer, scaler):
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/random_forest_model.pkl")
    joblib.dump(imputer, "models/imputer.pkl")
    joblib.dump(scaler, "models/scaler.pkl")
    print("Model and preprocessing objects saved successfully!")
