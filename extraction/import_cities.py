import pandas as pd

def load_cities_from_csv(file):
    return pd.read_csv(file)


def filter_by_country(country, df):
    return df[df['country']==country]