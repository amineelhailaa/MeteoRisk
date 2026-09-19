
import numpy as np
import pandas as pd
from pathlib import Path

from transformation.categories import add_weather_categories


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BRONZE_PATH = PROJECT_ROOT / "data" / "bronze" / "bronze_meteo_data.csv"
SILVER_PATH = PROJECT_ROOT / "data" / "silver" / "gold_meteo_data.csv"


def inspect_dataframe(df):
    print("=" * 60)
    print("DATA SUMMARY")
    print("=" * 60)
    print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")
    print(f"Duplicated rows: {df.duplicated().sum()}")
    print("=" * 60)
    print(df.describe())
    print("=" * 60)
    print(df.dtypes)
    print("=" * 60)
    print(df.isna().sum())


def to_string(df, *columns):
    return df.assign(
        **{
            column: df[column].astype("string").str.strip()
            for column in columns
        }
    )


def to_numeric(df, *columns):
    def convert(series):
        return pd.to_numeric(
            series.astype(str).str.replace(",", "", regex=False).str.strip(),
            errors="coerce",
        )

    return df.assign(
        **{column: convert(df[column]) for column in columns}
    )


def to_datetime(df, *columns):
    return df.assign(
        **{column: pd.to_datetime(df[column]) for column in columns}
    )


def get_weather_score(risk_score, weather_code):
    weather_quality = {
        0: 100,
        1: 100,
        2: 90,
        3: 80,
        45: 60,
        48: 60,
        51: 75,
        53: 70,
        55: 65,
        61: 55,
        63: 45,
        65: 30,
        66: 25,
        67: 20,
        71: 35,
        73: 25,
        75: 15,
        77: 20,
        80: 45,
        81: 35,
        82: 25,
        85: 20,
        86: 10,
        95: 10,
        96: 0,
        99: 0,
    }

    code_quality = weather_quality.get(weather_code, 50)
    risk_quality = 100 - risk_score

    return round(0.7 * risk_quality + 0.3 * code_quality, 2)


def get_risk_score(
    precipitation_sum,
    temperature_max,
    wind_speed_max,
    wind_gusts_max,
    temperature_min,
):
    rain = np.clip(precipitation_sum / 30, 0, 1)
    heat = np.clip((temperature_max - 35) / 10, 0, 1)
    cold = np.clip(-temperature_min / 10, 0, 1)
    temperature = max(heat, cold)
    wind = np.clip(wind_speed_max / 80, 0, 1)
    gusts = np.clip(wind_gusts_max / 100, 0, 1)

    score = 100 * max(rain, temperature, wind, gusts)

    return round(score, 2)


def fix_min_max(df, column_pairs):
    df = df.copy()

    for min_column, max_column in column_pairs:
        wrong_order = df[min_column] > df[max_column]
        df.loc[wrong_order, [min_column, max_column]] = (
            df.loc[wrong_order, [max_column, min_column]].to_numpy()
        )

    return df


def transform_weather_data(
    input_path=BRONZE_PATH,
    output_path=SILVER_PATH,
):
    df = pd.read_csv(input_path)

    df = to_string(df, "city", "country")
    df = to_numeric(
        df,
        "latitude",
        "longitude",
        "temperature_max",
        "temperature_min",
        "precipitation_sum",
        "precipitation_probability_max",
        "wind_speed_10m_max",
        "wind_gusts_10m_max",
        "weather_code",
    )
    df = to_datetime(df, "forecast_date")
    df = fix_min_max(df, [("temperature_min", "temperature_max")])

    df = df.drop_duplicates(
        subset=["city", "forecast_date"],
        keep="last",
    )

    df["risk_score"] = df.apply(
        lambda row: get_risk_score(
            row["precipitation_sum"],
            row["temperature_max"],
            row["wind_speed_10m_max"],
            row["wind_gusts_10m_max"],
            row["temperature_min"],
        ),
        axis=1,
    )

    df["weather_score"] = df.apply(
        lambda row: get_weather_score(
            row["risk_score"],
            row["weather_code"],
        ),
        axis=1,
    )

    df = add_weather_categories(df)
    df.to_csv(output_path, index=False)

    return output_path
