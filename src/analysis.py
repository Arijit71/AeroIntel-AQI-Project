import pandas as pd



def basic_statistics(df):
    """
    Display basic statistical summary of numerical columns.
    """

    print("\n" + "=" * 50)
    print("BASIC STATISTICS")
    print("=" * 50)

    print(df.describe())


def check_missing_values(df):
    """
    Check for remaining missing values.
    """

    print("\n" + "=" * 50)
    print("MISSING VALUES")
    print("=" * 50)

    print(df.isnull().sum())


def analyze_aqi(df):
    """
    Display statistical information about AQI.
    """

    print("\n" + "=" * 50)
    print("AQI ANALYSIS")
    print("=" * 50)

    print("Minimum AQI:", df["AQI"].min())
    print("Maximum AQI:", df["AQI"].max())
    print("Average AQI:", df["AQI"].mean())
    print("Median AQI:", df["AQI"].median())
    print("Standard Deviation:", df["AQI"].std())

def analyze(df):
    basic_statistics(df)
    analyze_aqi(df)
