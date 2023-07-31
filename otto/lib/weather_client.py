from datetime import datetime
from http import HTTPStatus
from typing import Final, Self

import aiohttp

from otto import logger as root_logger
from otto.constants import DEFAULT_TIMEOUT
from otto.models.weather import Weather, is_links_dict, is_weather_dict
from otto.utils import get_now
from otto.utils.convert import convert_tzstring

logger: Final = root_logger.getChild("weather_client")


class WeatherClient:
    """A client for getting weather data from the National Weather Service."""

    async def get_weather(self: Self, lat: float, long: float, date: datetime | None = None) -> Weather | None:
        """Get the weather at a location and time."""
        url = f"https://api.weather.gov/points/{lat:.4f},{long:.4f}"
        date = date or get_now()

        async with (
            aiohttp.ClientSession() as session,
            session.get(url, timeout=DEFAULT_TIMEOUT) as res,
        ):
            links = await res.json() if res.status == HTTPStatus.OK else {}
            forecast_url = links["properties"]["forecast"] if is_links_dict(links) else ""

        if forecast_url:
            async with (
                aiohttp.ClientSession() as session,
                session.get(forecast_url, timeout=DEFAULT_TIMEOUT) as res,
            ):
                weather = await res.json() if res.status == HTTPStatus.OK else {}
                periods = weather["properties"]["periods"] if is_weather_dict(weather) else []

            for period in periods:
                forecast_start = convert_tzstring(period["startTime"])
                forecast_end = convert_tzstring(period["endTime"])

                if forecast_start <= date <= forecast_end:
                    return Weather.from_nws_period_dict(period)
        return None
