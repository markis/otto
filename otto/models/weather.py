from typing import Any, Final, Self, TypeGuard, TypedDict


class LinksPropertiesDict(TypedDict):
    """Weather information links from the National Weather Service."""

    forecast: str
    forecastHourly: str


class LinksDict(TypedDict):
    """Weather information from the National Weather Service."""

    properties: LinksPropertiesDict


class WeatherPeriodDict(TypedDict):
    """TypedDict for the properties of the periods field."""

    startTime: str
    endTime: str
    isDaytime: bool
    temperature: int
    temperatureUnit: str
    dewpoint: dict[str, Any]
    relativeHumidity: dict[str, Any]
    windSpeed: str
    windDirection: str
    shortForecast: str


class WeatherPropertiesDict(TypedDict):
    """Weather information from the National Weather Service."""

    updated: str
    units: str
    forecastGenerator: str
    generatedAt: str
    updateTime: str
    validTimes: str
    periods: list[WeatherPeriodDict]


class WeatherDict(TypedDict):
    """Weather information from the National Weather Service."""

    properties: WeatherPropertiesDict


def is_links_dict(value: object) -> TypeGuard[LinksDict]:
    """Determine if data is LinksDict."""
    return isinstance(value, dict) and "properties" in value and "forecast" in value["properties"]


def is_weather_dict(value: object) -> TypeGuard[WeatherDict]:
    """Determine if data is LinksDict."""
    return isinstance(value, dict) and "properties" in value and "periods" in value["properties"]


class Weather:
    """A class representing the weather at a specific time."""

    forecast: Final[str]
    temperature: Final[int]
    wind_speed: Final[str]
    wind_direction: Final[str]

    def __init__(self: Self, forecast: str, temperature: int, wind_direction: str, wind_speed: str) -> None:
        """Initialize a Weather object."""
        self.forecast = forecast
        self.temperature = temperature
        self.wind_direction = wind_direction
        self.wind_speed = wind_speed

    @classmethod
    def from_nws_period_dict(cls, data: WeatherPeriodDict) -> Self:  # noqa: ANN102
        """Initialize a Weather object from the National Weather Service."""
        return cls(data["shortForecast"], int(data["temperature"]), data["windDirection"], data["windSpeed"])
