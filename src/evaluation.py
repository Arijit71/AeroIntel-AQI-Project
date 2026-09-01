import numpy as np

from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score


def evaluate_model(model, X_test, y_test):
    """
    Evaluate the trained AQI prediction model.
    """

    # Predict AQI values
    y_pred = model.predict(X_test)

    # Calculate MAE
    mae = mean_absolute_error(y_test, y_pred)

    # Calculate MSE
    mse = mean_squared_error(y_test, y_pred)

    # Calculate RMSE
    rmse = np.sqrt(mse)

    # Calculate R² Score
    r2 = r2_score(y_test, y_pred)

    # Print results
    print("\nMODEL EVALUATION")
    print("-" * 30)

    print(f"MAE: {mae:.2f}")
    print(f"MSE: {mse:.2f}")
    print(f"RMSE: {rmse:.2f}")
    print(f"R² Score: {r2:.4f}")

    return y_pred