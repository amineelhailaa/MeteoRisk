
import pandas as pd

def add_weather_categories(df):
    df = df.copy()
    df["temp_category"] = pd.cut(
        df["temperature_max"],
        bins=[-float("inf"), 0, 10, 20, 34, float("inf")],
        labels=["Very Cold", "Cold", "Cool", "Comfortable", "Hot"],
    )
    df["precipitation_category"] = pd.cut(
        df["precipitation_sum"],
        bins=[-float("inf"), 0, 2.5, 10, 50, float("inf")],
        labels=["No Rain", "Light", "Moderate", "Heavy", "Very Heavy"],
    )
    df["wind_category"] = pd.cut(
        df["wind_speed_10m_max"],
        bins=[-float("inf"), 5, 20, 40, 60, float("inf")],
        labels=["Calm", "Light", "Moderate", "Strong", "Very Strong"],
    )
    return df

