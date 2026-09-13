import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_indian_city_day_dataset():
    os.makedirs("data/raw", exist_ok=True)
    file_path = "data/raw/city_day.csv"

    cities = ["Delhi", "Mumbai", "Bengaluru", "Kolkata", "Chennai", "Hyderabad", "Ahmedabad", "Lucknow"]
    start_date = datetime(2018, 1, 1)
    n_days = 365 * 2 # 2 years of daily data per city

    city_baselines = {
        "Delhi": {"pm25": 115, "pm10": 210, "no2": 45, "so2": 18, "co": 1.4, "o3": 40},
        "Mumbai": {"pm25": 55, "pm10": 95, "no2": 30, "so2": 15, "co": 0.9, "o3": 28},
        "Bengaluru": {"pm25": 38, "pm10": 65, "no2": 22, "so2": 9, "co": 0.7, "o3": 25},
        "Kolkata": {"pm25": 75, "pm10": 130, "no2": 38, "so2": 14, "co": 1.1, "o3": 32},
        "Chennai": {"pm25": 42, "pm10": 72, "no2": 20, "so2": 11, "co": 0.7, "o3": 26},
        "Hyderabad": {"pm25": 50, "pm10": 90, "no2": 26, "so2": 12, "co": 0.8, "o3": 30},
        "Ahmedabad": {"pm25": 70, "pm10": 125, "no2": 40, "so2": 22, "co": 1.2, "o3": 35},
        "Lucknow": {"pm25": 105, "pm10": 190, "no2": 35, "so2": 16, "co": 1.3, "o3": 38},
    }

    rows = []
    np.random.seed(42)

    for city in cities:
        base = city_baselines[city]
        for day_offset in range(n_days):
            current_date = start_date + timedelta(days=day_offset)
            # Seasonal winter peak (Nov - Feb)
            month = current_date.month
            seasonal_factor = 1.6 if month in [11, 12, 1, 2] else (0.75 if month in [7, 8, 9] else 1.0)

            # Generate realistic correlated pollutants
            noise = np.random.normal(0, 0.15)
            pm25 = max(5.0, round(base["pm25"] * seasonal_factor * (1 + noise), 2))
            pm10 = max(pm25 * 1.2, round(base["pm10"] * seasonal_factor * (1 + np.random.normal(0, 0.12)), 2))
            no = max(1.0, round(pm25 * 0.2 + np.random.normal(0, 3), 2))
            no2 = max(2.0, round(base["no2"] * (1 + np.random.normal(0, 0.15)), 2))
            nox = max(no + no2 * 0.8, round(no + no2 + np.random.normal(0, 4), 2))
            nh3 = max(1.0, round(pm25 * 0.25 + np.random.normal(0, 4), 2))
            co = max(0.1, round(base["co"] * (1 + np.random.normal(0, 0.15)), 2))
            so2 = max(1.0, round(base["so2"] * (1 + np.random.normal(0, 0.18)), 2))
            o3 = max(2.0, round(base["o3"] * (1 + np.random.normal(0, 0.2)), 2))
            benzene = max(0.05, round(pm25 * 0.03 + np.random.normal(0, 0.5), 2))
            toluene = max(0.1, round(pm25 * 0.06 + np.random.normal(0, 0.8), 2))
            # Xylene has >50% missing values as typical in Kaggle dataset
            xylene = round(pm25 * 0.04 + np.random.normal(0, 0.5), 2) if np.random.rand() > 0.6 else np.nan

            # Calculate realistic AQI heavily weighted on PM2.5 and PM10
            aqi_est = max(pm25 * 1.3, pm10 * 0.85, no2 * 1.1) + np.random.normal(0, 8)
            aqi = min(490.0, max(15.0, round(aqi_est, 1)))

            # AQI Bucket
            if aqi <= 50:
                bucket = "Good"
            elif aqi <= 100:
                bucket = "Satisfactory"
            elif aqi <= 200:
                bucket = "Moderate"
            elif aqi <= 300:
                bucket = "Poor"
            elif aqi <= 400:
                bucket = "Very Poor"
            else:
                bucket = "Severe"

            # 2% random missing values in pollutants to test interpolation
            if np.random.rand() < 0.03:
                pm25 = np.nan

            rows.append({
                "City": city,
                "Date": current_date.strftime("%Y-%m-%d"),
                "PM2.5": pm25,
                "PM10": pm10,
                "NO": no,
                "NO2": no2,
                "NOx": nox,
                "NH3": nh3,
                "CO": co,
                "SO2": so2,
                "O3": o3,
                "Benzene": benzene,
                "Toluene": toluene,
                "Xylene": xylene,
                "AQI": aqi,
                "AQI_Bucket": bucket
            })

    df = pd.DataFrame(rows)
    df.to_csv(file_path, index=False)
    print(f"Dataset generated at {file_path} with {len(df)} records across {len(cities)} cities.")

if __name__ == "__main__":
    generate_indian_city_day_dataset()
