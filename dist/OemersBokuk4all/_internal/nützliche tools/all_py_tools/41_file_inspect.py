import pandas as pd


def file_inspect(file):
    df = pd.read_csv(file) if file.endswith('.csv') else pd.read_excel(file)
    print(df.head())
    print("Columns:", df.columns)
