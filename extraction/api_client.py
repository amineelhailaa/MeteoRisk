from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class ApiClient(ABC):
    URL: str

    @abstractmethod
    def get_data_from_all_cities(self):
        pass


    @abstractmethod
    def get_data_from_this_cities(self, cors):
        pass

    @abstractmethod
    def get_data_from_this_city(self, cor):
        pass

    @abstractmethod
    def is_api_working(self) ->bool:
        pass