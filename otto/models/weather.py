from typing import Dict


class Weather(object):
    forecast: str
    temperature: int
    wind_speed: str
    wind_direction: str

    def __init__(self, data: Dict[str, str]):
        self.forecast = data["shortForecast"]
        self.temperature = int(data["temperature"])
        self.wind_direction = data["windDirection"]
        self.wind_speed = data["windSpeed"]
