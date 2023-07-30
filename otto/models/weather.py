from typing import Any, Final, Self, TypedDict


class WeatherLinksDict(TypedDict):
    """Weather information links from the National Weather Service."""

    cwa: str
    forecastOffice: str
    gridId: str
    gridX: int
    gridY: int
    forecast: str
    forecastHourly: str
    forecastGridData: str
    observationStations: str
    forecastZone: str
    county: str
    fireWeatherZone: str
    timeZone: str
    radarStation: str


class LinksJSON(TypedDict):
    """Weather information from the National Weather Service."""

    id: str
    type: str
    properties: WeatherLinksDict


class WeatherPeriodDict(TypedDict):
    """TypedDict for the properties of the periods field."""

    number: int
    name: str
    startTime: str
    endTime: str
    isDaytime: bool
    temperature: int
    temperatureUnit: str
    temperatureTrend: str | None
    probabilityOfPrecipitation: dict[str, Any] | None
    dewpoint: dict[str, Any]
    relativeHumidity: dict[str, Any]
    windSpeed: str
    windDirection: str
    icon: str
    shortForecast: str
    detailedForecast: str


class ElevationDict(TypedDict):
    """TypedDict for the properties of the elevation field."""

    unitCode: str
    value: float


class WeatherPropertiesDict(TypedDict):
    """Weather information from the National Weather Service."""

    updated: str
    units: str
    forecastGenerator: str
    generatedAt: str
    updateTime: str
    validTimes: str
    elevation: ElevationDict
    periods: list[WeatherPeriodDict]


class WeatherData(TypedDict):
    """Weather information from the National Weather Service."""

    type: str
    properties: WeatherPropertiesDict


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
