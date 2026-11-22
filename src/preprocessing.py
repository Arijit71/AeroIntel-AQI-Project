import pandas as pd

POLLUTANT_COLUMNS = [
    "PM2.5", "PM10", "NO", "NO2", "NOx",
    "NH3", "CO", "SO2", "O3", "Benzene", "Toluene", "Xylene"
]


def convert_date(df):
    df["Date"] = pd.to_datetime(df["Date"])
    return df


def sort_data(df):
    return df.sort_values(["City", "Date"]).reset_index(drop=True)


def interpolate_values(df):
    cols = [c for c in POLLUTANT_COLUMNS if c in df.columns]
    df[cols] = df.groupby("City")[cols].transform(lambda g: g.interpolate(method="linear"))
    return df


def drop_unnecessary_columns(df):
    if "AQI_Bucket" in df.columns:
        df = df.drop(columns=["AQI_Bucket"])
    return df


def fill_remaining_values(df):
    cols = [c for c in POLLUTANT_COLUMNS if c in df.columns]
    for col in cols:
        df[col] = df.groupby("City")[col].transform(lambda g: g.fillna(g.median()))
        df[col] = df[col].fillna(df[col].median())
    return df


def remove_missing_target(df):
    return df.dropna(subset=["AQI"])


def preprocess_data(df):
    df = convert_date(df)
    df = sort_data(df)

    # Drop columns with >50% missing values
    missing = df.isnull().sum()
    columns_to_drop = missing[(missing / len(df) * 100) > 50].index
    if len(columns_to_drop) > 0:
        df = df.drop(columns=columns_to_drop)
        print(f"✓ Dropped sparse columns (>50% missing): {list(columns_to_drop)}")

    df = interpolate_values(df)
    df = drop_unnecessary_columns(df)
    df = fill_remaining_values(df)
    df = remove_missing_target(df)

    # One-hot encode cities and extract date components
    df = pd.get_dummies(df, columns=["City"], drop_first=True)
    bool_cols = df.select_dtypes(include="bool").columns
    df[bool_cols] = df[bool_cols].astype(int)

    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["Day"] = df["Date"].dt.day
    df = df.drop(columns=["Date"])

    # Remove outlier AQI above standard ceiling
    return df.drop(df[df["AQI"] > 500].index)
