import pandas as pd
from pathlib import Path


def load_data(file_path):
    """
    Load the air quality dataset from a CSV file.
    """
    df = pd.read_csv(file_path)

    return df


def inspect_data(df):

    print("\n===== DATASET SHAPE =====")
    print(df.shape)

    print("\n===== COLUMN NAMES =====")
    print(df.columns.tolist())

    print("\n===== FIRST 5 ROWS =====")
    print(df.head())

    print("\n===== DATA TYPES =====")
    print(df.dtypes)

    print("\n===== MISSING VALUES =====")
    print(df.isnull().sum())

    print("\n===== BASIC STATISTICS =====")
    print(df.describe())

    print("\n===== DUPLICATE ROWS =====")
    print(df.duplicated().sum())

    print("\n===== UNIQUE CITIES =====")
    print(df["City"].nunique())

    print("\n===== CITY COUNTS =====")
    print(df["City"].value_counts())