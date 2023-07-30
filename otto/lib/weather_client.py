from datetime import datetime
from typing import Final, Self

import aiohttp

from otto import logger as root_logger
from otto.constants import DEFAULT_TIMEOUT
from otto.models.weather import Weather
from otto.utils import get_now
from otto.utils.convert import convert_tzstring

logger: Final = root_logger.getChild("weather_client")


class WeatherClient:
    """A client for getting weather data from the National Weather Service."""

    async def get_weather(self: Self, lat: float, long: float, date: datetime | None = None) -> Weather | None:
        """Get the weather at a location and time."""
        url = f"https://api.weather.gov/points/{lat},{long}"
        date = date or get_now()
        async with (
            aiohttp.ClientSession() as session,
            session.get(url, timeout=DEFAULT_TIMEOUT) as res,
        ):
            links = await res.json()

        if links and (forecast_url := links.get("properties", {}).get("forecast")):
            async with (
                aiohttp.ClientSession() as session,
                session.get(forecast_url, timeout=DEFAULT_TIMEOUT) as res,
            ):
                weather = await res.json()

            periods = weather["properties"]["periods"]
            for period in periods:
                forecast_start = convert_tzstring(period["startTime"])
                forecast_end = convert_tzstring(period["endTime"])

                if forecast_start <= date and forecast_end >= date:
                    return Weather.from_nws_period_dict(period)
        return None
