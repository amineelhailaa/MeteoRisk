"""Load a transformed Pandas DataFrame with SQLAlchemy ORM."""

import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from load.models import (
    Base,
    City,
    Forecast,
    Precipitation,
    RiskAssessment,
    Temperature,
    Wind,
)


DATABASE_URL = os.getenv("METEORISK_DB_URL")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GOLD_PATH = PROJECT_ROOT / "data" / "gold" / "gold_meteo_data.csv"


def create_tables() -> None:
    Base.metadata.create_all(engine)


def load_weather_dataframe(df: pd.DataFrame) -> int:
    already_processed = {}
    with Session(engine) as session:
        try:
            for row in df.itertuples(index=False):
                city_key = (
                    str(row.city).strip(),
                    str(row.country).strip(),
                    round(float(row.latitude), 6),
                    round(float(row.longitude), 6),
                )

                city = already_processed.get(city_key)
                if city is None:
                    city = session.query(City).filter_by(
                        name=city_key[0],
                        country=city_key[1],
                        latitude=city_key[2],
                        longitude=city_key[3],
                    ).one_or_none()

                    if city is None:
                        city = City(
                            name=city_key[0],
                            country=city_key[1],
                            latitude=city_key[2],
                            longitude=city_key[3],
                        )
                        session.add(city)
                        session.flush()
                    already_processed[city_key] = city

                forecast_date = pd.to_datetime(row.forecast_date).date()
                source = _optional(row, "source") or "ara dik lid"

                forecast = session.query(Forecast).filter_by(
                    city_id=city.id,
                    forecast_date=forecast_date,
                    source=source,
                ).one_or_none()

                if forecast is None:
                    forecast = Forecast(
                        city=city,
                        forecast_date=forecast_date,
                        source=source,
                    )
                    session.add(forecast)

                forecast.extracted_at = _extracted_at(row)
                forecast.weather_code = int(row.weather_code)

                if forecast.temperature is None:
                    forecast.temperature = Temperature()
                forecast.temperature.temperature_min = row.temperature_min
                forecast.temperature.temperature_max = row.temperature_max
                forecast.temperature.category = _optional(row, "temp_category")

                if forecast.precipitation is None:
                    forecast.precipitation = Precipitation()
                forecast.precipitation.precipitation_sum = row.precipitation_sum
                forecast.precipitation.probability_max = row.precipitation_probability_max

                forecast.precipitation.category = _optional(
                    row,
                    "precipitation_category",
                )

                if forecast.wind is None:
                    forecast.wind = Wind()
                forecast.wind.speed_10m_max = float(row.wind_speed_10m_max)
                forecast.wind.gusts_10m_max = float(row.wind_gusts_10m_max)
                forecast.wind.category = _optional(row, "wind_category")

                if forecast.risk_assessment is None:
                    forecast.risk_assessment = RiskAssessment()
                forecast.risk_assessment.risk_score = float(row.risk_score)
                forecast.risk_assessment.weather_score = _optional(
                    row,
                    "weather_score",
                )
                forecast.risk_assessment.risk_level = _optional(row, "risk_level")

            session.commit()
        except Exception:
            session.rollback()
            raise

    return len(df)


def _optional(row, column: str):

    value = getattr(row, column, None)
    if value is None or pd.isna(value):
        return None
    return value


def _extracted_at(row) -> datetime:
    value = _optional(row, "extracted_at")
    if value is None:
        return datetime.now(timezone.utc)
    return pd.to_datetime(value, utc=True).to_pydatetime()






def load_weather_csv(csv_path=GOLD_PATH):
    df = pd.read_csv(csv_path)
    create_tables()
    return load_weather_dataframe(df)
