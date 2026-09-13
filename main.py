from src.data_loader import load_data,inspect_data
from src.preprocessing import preprocess_data
from src.analysis import *
from src.visualization import *
from src.feature_engineering import *
from src.model_training import *
from src.evaluation import evaluate_model
from src.model_saving import *
from src.predict import *

import pandas as pd


def main():

    file_path = "data/raw/city_day.csv"

    # Load raw dataset
    df = load_data(file_path)
    inspect_data(df)

    # Preprocess
    df = preprocess_data(df)
    pd.set_option("display.max_columns", None)

    print("\nCleaned data:\n",df.head(10))
    import os
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv("data/processed/cleaned_city_day.csv", index=False)

    analyze(df)
    visualize(df)

    # Prepare features
    X_train, X_test, y_train, y_test,imputer,scaler = prepare_features()


    # Train model
    model = train_random_forest(
        X_train,
        y_train
    )


    print("Model trained successfully!")

    y_pred = evaluate_model(
        model,
        X_test,
        y_test
    )

    # Feature names
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


    # Plot feature importance
    plot_feature_importance(
        model,
        features
    )

    plot_actual_vs_predicted(y_test,y_pred)

    save_model(
        model,
        imputer,
        scaler
    )




    #predicting AQI from new data
    new_data = {
    "PM2.5": 85,
    "PM10": 120,
    "NO": 15,
    "NO2": 30,
    "NOx": 40,
    "NH3": 20,
    "CO": 1.2,
    "SO2": 10,
    "O3": 35,
    "Benzene": 2.5,
    "Toluene": 5
    }

    predicted_aqi = predict_aqi(new_data)

    print(f"\nPredicted AQI: {predicted_aqi:.2f}")
    

if __name__ == "__main__":
    main()