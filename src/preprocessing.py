import pandas as pd


def convert_date(df):
    """
    Convert Date column from string to datetime.
    """

    df["Date"] = pd.to_datetime(df["Date"])

    return df


def sort_data(df):
    """
    Sort data by city and date.
    """

    df = df.sort_values(["City", "Date"]).reset_index(drop=True)

    return df


def interpolate_values(df):
    """
    Interpolate missing pollutant values within each city.
    """

    feature_columns = [
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
        "Toluene",
        "Xylene"
    ]

    df[feature_columns] = (
        df.groupby("City")[feature_columns]
        .transform(
            lambda group: group.interpolate(method="linear")
        )
    )

    return df


def drop_unnecessary_columns(df):
    """
    Remove columns that we will not use for the ML model.
    """

    df = df.drop(columns=["AQI_Bucket"])

    return df


def fill_remaining_values(df):
    """
    Fill remaining missing pollutant values
    using the median of each city.
    """

    feature_columns = [
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

    for column in feature_columns:

        # df[column] = df.groupby("City")[column].transform(
        #     lambda group: group.fillna(group.median())
        # )

        df[column]=df[column].fillna(df[column].median())

    return df


def remove_missing_target(df):
    """
    Remove rows where AQI target is missing.
    """

    df = df.dropna(subset=["AQI"])

    return df


def preprocess_data(df):

    df = convert_date(df)

    df = sort_data(df)

    df = interpolate_values(df)

    feature_columns = [
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
        "Toluene",
        "Xylene"
    ]

    missing = df.isnull().sum()
    columns_to_drop = missing[(missing / len(df) * 100) > 50].index
    print("\nColumns having null value greater than 50%:",columns_to_drop,"\n")
    df=df.drop(columns=columns_to_drop)
    print(f"{columns_to_drop.values} dropped successfully")

    df=drop_unnecessary_columns(df)

    df = fill_remaining_values(df)

    df = remove_missing_target(df)

    df=pd.get_dummies(df,columns=["City"],drop_first=True)
    bool_columns = df.select_dtypes(include="bool").columns
    df[bool_columns] = df[bool_columns].astype(int)

    df["Year"] = df["Date"].dt.year
    df["Month"] = df["Date"].dt.month
    df["Day"] = df["Date"].dt.day
    df = df.drop(columns=["Date"])

    df=df.drop(df[df["AQI"]>500].index)

    return df