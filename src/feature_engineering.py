import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

FEATURES = [
    "PM2.5", "PM10", "NO", "NO2", "NOx",
    "NH3", "CO", "SO2", "O3", "Benzene", "Toluene"
]


def prepare_features(df=None, test_size=0.2):
    if df is None:
        df = pd.read_csv("data/processed/cleaned_city_day.csv")

    df = df.dropna(subset=["AQI"])
    X = df[FEATURES]
    y = df["AQI"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42
    )

    imputer = SimpleImputer(strategy="median")
    X_train = imputer.fit_transform(X_train)
    X_test = imputer.transform(X_test)

    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    return X_train, X_test, y_train, y_test, imputer, scaler


def prepare_full_dataset(df=None):
    if df is None:
        df = pd.read_csv("data/processed/cleaned_city_day.csv")

    df = df.dropna(subset=["AQI"])
    X = df[FEATURES]
    y = df["AQI"]

    imputer = SimpleImputer(strategy="median")
    X_imputed = imputer.fit_transform(X)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_imputed)

    return X_scaled, y, imputer, scaler
