import os
from datetime import date
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session
from load.models import *
import matplotlib.pyplot as plt

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "meteorisk_db")
DB_USER = os.getenv("DB_USER", "meteorisk_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "meteorisk")
DATABASE_URL = (
    f"postgresql+psycopg2://"
    f"{DB_USER}:{DB_PASSWORD}@"
    f"{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
engine = create_engine(DATABASE_URL)






st.set_page_config(page_title="MeteoRisk Data Analyst", layout="wide")



with Session(engine) as session:

    all_data = select(City, Forecast, Temperature, Wind, RiskAssessment)
    stmt_max_temp = select(func.max(Temperature.temperature_max)).join(Temperature.forecast).where(Forecast.forecast_date == date.today())
    stmt_min_temp = select(func.min(Temperature.temperature_min)).join(Temperature.forecast).where(Forecast.forecast_date == date.today())
    stmt_wind_speed = select(func.max(Wind.speed_10m_max)).join(Wind.forecast).where(Forecast.forecast_date == date.today())
    stmt_wind_gust = select(func.max(Wind.gusts_10m_max)).join(Wind.forecast).where(Forecast.forecast_date == date.today())
    stmt_most_sunny = select(City.name).join(City.forecasts).join(Forecast.temperature).order_by(Temperature.temperature_max.desc()).limit(1)
    stmt_city_highest_risk = select(City.name).join(City.forecasts).join(Forecast.risk_assessment).order_by(RiskAssessment.risk_score.desc()).limit(1)
    max_temp = session.execute(stmt_max_temp).scalar()
    min_temp = session.execute(stmt_min_temp).scalar()
    max_wind_speed = session.execute(stmt_wind_speed).scalar()
    max_wind_gust = session.execute(stmt_wind_gust).scalar()
    most_sunny_city = session.execute(stmt_most_sunny).scalar()
    session.close()
















st.title("MeteoRisk Dashboard")
st.subheader("Weather Overview")

col1, col2, col3, col4, col5 = st.columns(5)


col1.metric(
    "Maximum Temperature",
    f"{max_temp:.1f}°C" if max_temp is not None else "N/A"
)

col2.metric(
    "Minimum temperature",
    f"{min_temp:.1f} °C" if min_temp is not None else "N/A",
)

col3.metric(
    "Maximum wind speed",
    f"{max_wind_speed:.1f} km/h"
    if max_wind_speed is not None
    else "N/A",
)

col4.metric(
    "Maximum wind gust",
    f"{max_wind_gust:.1f} km/h"
    if max_wind_gust is not None
    else "N/A",
)

col5.metric(
    "Hottest city",
    most_sunny_city if most_sunny_city else "N/A",
)




def load_filter_options():
    with Session(engine) as session:
        cities = session.execute(
            select(City.name)
            .distinct()
            .order_by(City.name)
        ).scalars().all()

        min_date, max_date = session.execute(
            select(
                func.min(Forecast.forecast_date),
                func.max(Forecast.forecast_date),
            )
        ).one()

    return cities, min_date, max_date




@st.cache_data(ttl=600)
def load_trend_data(city, start_date, end_date):
    with Session(engine) as session:
        stmt = (
            select(
                Forecast.forecast_date.label("date"),

                func.max(
                    Temperature.temperature_max
                ).label("max_temp"),

                func.min(
                    Temperature.temperature_min
                ).label("min_temp"),

                func.avg(
                    Precipitation.precipitation_sum
                ).label("precipitation"),

                func.max(
                    Wind.speed_10m_max
                ).label("max_wind"),

                func.max(
                    Wind.gusts_10m_max
                ).label("max_gust"),
            )
            .select_from(Forecast)
            .join(Forecast.city)
            .join(Forecast.temperature)
            .join(Forecast.precipitation)
            .join(Forecast.wind)
            .where(
                Forecast.forecast_date >= start_date,
                Forecast.forecast_date <= end_date,
            )
            .group_by(Forecast.forecast_date)
            .order_by(Forecast.forecast_date)
        )

        if city != "All cities":
            stmt = stmt.where(City.name == city)

        rows = session.execute(stmt).mappings().all()

    return pd.DataFrame(rows)



cities, min_date, max_date = load_filter_options()

if min_date is None or max_date is None:
    st.warning("No forecast data is available.")
    st.stop()

selected_city = st.sidebar.selectbox(
    "City",
    ["All cities"] + list(cities),
)

selected_dates = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

if len(selected_dates) != 2:
    st.info("Select both a start date and an end date.")
    st.stop()

start_date, end_date = selected_dates


trend_df = load_trend_data(
    city=selected_city,
    start_date=start_date,
    end_date=end_date,
)

if trend_df.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

trend_df["date"] = pd.to_datetime(trend_df["date"])



st.subheader("Weather trend over time")

chart_type = st.selectbox(
    "Select weather measurement",
    ["Temperature", "Precipitation", "Wind"],
)

fig, ax = plt.subplots(figsize=(12, 5))

if chart_type == "Temperature":
    ax.plot(
        trend_df["date"],
        trend_df["max_temp"],
        marker="o",
        label="Maximum temperature",
    )

    ax.plot(
        trend_df["date"],
        trend_df["min_temp"],
        marker="o",
        label="Minimum temperature",
    )

    ax.set_title("Temperature trend")
    ax.set_ylabel("Temperature (°C)")

elif chart_type == "Precipitation":
    ax.plot(
        trend_df["date"],
        trend_df["precipitation"],
        marker="o",
        color="royalblue",
        label="Average precipitation",
    )

    ax.set_title("Precipitation trend")
    ax.set_ylabel("Precipitation (mm)")

else:
    ax.plot(
        trend_df["date"],
        trend_df["max_wind"],
        marker="o",
        label="Maximum wind speed",
    )

    ax.plot(
        trend_df["date"],
        trend_df["max_gust"],
        marker="o",
        label="Maximum wind gust",
    )

    ax.set_title("Wind trend")
    ax.set_ylabel("Wind speed (km/h)")

ax.set_xlabel("Date")
ax.legend()
ax.grid(alpha=0.3)

fig.autofmt_xdate()
fig.tight_layout()

st.pyplot(fig)
plt.close(fig)




