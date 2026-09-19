from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from extraction.import_cities import filter_by_country, load_cities_from_csv
from extraction.openmeteo_apiclient import OpenMeteoApi


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CITIES_PATH = PROJECT_ROOT / "data" / "bronze" / "worldcities.csv"
BRONZE_PATH = PROJECT_ROOT / "data" / "bronze" / "bronze_meteo_data.csv"




def extract_weather_forecasts(cities, client):
    frames = []

    for city in cities.itertuples(index=False):
        try:
            weather = client.get_data_from_this_city(
                latitude=str(city.lat),
                longitude=str(city.lng),
            )

            daily = weather["daily"]
            frames.append(
                pd.DataFrame(
                    {
                        "city": city.city,
                        "country": city.country,
                        "latitude": city.lat,
                        "longitude": city.lng,
                        "forecast_date": daily["time"],
                        "extracted_at": datetime.now(timezone.utc),
                        "temperature_max": daily["temperature_2m_max"],
                        "temperature_min": daily["temperature_2m_min"],
                        "precipitation_sum": daily["precipitation_sum"],
                        "precipitation_probability_max": daily[
                            "precipitation_probability_max"
                        ],
                        "wind_speed_10m_max": daily["wind_speed_10m_max"],
                        "wind_gusts_10m_max": daily["wind_gusts_10m_max"],
                        "weather_code": daily["weather_code"],
                        "source": "open-meteo",
                    }
                )
            )
        except Exception as error:
            print(f"Error fetching data for {city.city}: {error}")

    if not frames:
        return pd.DataFrame()

    return pd.concat(frames, ignore_index=True)


def execute_load():
    client = OpenMeteoApi()

    if not client.is_api_working():
        raise RuntimeError("OpenMeteo API is not working")

    cities = load_cities_from_csv(CITIES_PATH)
    moroccan_cities = filter_by_country("Morocco", cities)
    weather_df = extract_weather_forecasts(moroccan_cities, client)
    weather_df.to_csv(BRONZE_PATH, index=False)

    return str(BRONZE_PATH)
