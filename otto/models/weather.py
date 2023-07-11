from typing import Self


class Weather:
    """A class representing the weather at a specific time."""

    forecast: str
    temperature: int
    wind_speed: str
    wind_direction: str

    def __init__(self: Self, data: dict[str, str]) -> None:
        """Initialize a Weather object."""
        self.forecast = data["shortForecast"]
        self.temperature = int(data["temperature"])
        self.wind_direction = data["windDirection"]
        self.wind_speed = data["windSpeed"]
