import pandas as pd


def load_data(file_path):
    return pd.read_csv(file_path)


def inspect_data(df, verbose=False):
    if not verbose:
        print(f"✓ Dataset Loaded: {df.shape[0]:,} rows, {df.shape[1]} columns ({df['City'].nunique()} cities)")
        return

    print(f"Shape: {df.shape} | Cities: {df['City'].unique().tolist()}")
    print(f"Missing Values: {df.isnull().sum().to_dict()}")
