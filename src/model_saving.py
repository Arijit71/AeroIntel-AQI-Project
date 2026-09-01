import joblib
import os


def save_model(model, imputer, scaler):
    """
    Save the trained model and preprocessing objects.
    """

    # Create models folder if it does not exist
    os.makedirs("models", exist_ok=True)

    # Save Random Forest model
    joblib.dump(
        model,
        "models/random_forest_model.pkl"
    )

    # Save imputer
    joblib.dump(
        imputer,
        "models/imputer.pkl"
    )

    # Save scaler
    joblib.dump(
        scaler,
        "models/scaler.pkl"
    )

    print("\nModel and preprocessing objects saved successfully!")