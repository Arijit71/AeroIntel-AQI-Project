def analyze(df, verbose=False):
    missing_count = df.isnull().sum().sum()
    aqi_min = round(df["AQI"].min(), 1)
    aqi_max = round(df["AQI"].max(), 1)
    aqi_mean = round(df["AQI"].mean(), 1)

    print(f"✓ Data Quality Audit: {missing_count} missing values | AQI Range: [{aqi_min} — {aqi_max}] (Avg: {aqi_mean})")

    if verbose:
        print("\nBASIC STATISTICS\n" + "-" * 30)
        print(df.describe())
