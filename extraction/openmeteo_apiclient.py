from abc import ABC, abstractmethod
from typing import Any
from api_client import ApiClient


class OpenMeteoApi(ApiClient):

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    params = (
        "temperature_2m_max,"
        "temperature_2m_min,"
        "precipitation_sum,"
        "precipitation_probability_max,"
        "wind_speed_10m_max,"
        "wind_gusts_10m_max,"
        "weather_code"
    )

    period = "daily"

    def __init__(self):
        import requests
        self.session = requests.Session()



    def is_api_working(self) -> bool:
        try:
            response = self.session.get(
                self.BASE_URL,
                params={
                    "latitude": 33.5731,
                    "longitude": -7.5898,
                    "current": "temperature_2m",
                },
                timeout=5,
            )
    
            return response.ok
    
        except requests.RequestException:
            return False

        

    def get_data_from_this_city(
        self,
        latitude: float,
        longitude: float,
        forecast_days: int = 7
    ):


        parameters = {
            "latitude": latitude,
            "longitude": longitude,
            self.period : self.params,
            "forecast_days": forecast_days,
        }

        response =  self.session.get(self.BASE_URL, params= parameters )
        return response.json()
    def get_data_from_all_cities():
        pass
    def get_data_from_this_cities():
        pass