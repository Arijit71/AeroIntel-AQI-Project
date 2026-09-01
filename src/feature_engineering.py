import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


def prepare_features():
    """
    Load data and prepare features for machine learning.
    """

    # Load cleaned dataset
    df = pd.read_csv("data/processed/cleaned_city_day.csv")

    # Remove rows where AQI is missing
    df = df.dropna(subset=["AQI"])

    # Select input features
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

    # Features and target
    X = df[features]
    y = df["AQI"]

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    # Handle missing values
    imputer = SimpleImputer(strategy="median")

    X_train = imputer.fit_transform(X_train)
    X_test = imputer.transform(X_test)

    # Feature scaling
    scaler = StandardScaler()

    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    return X_train, X_test, y_train, y_test, imputer, scaler