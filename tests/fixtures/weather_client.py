from collections.abc import Iterable

import hypothesis.strategies as st
import pook
import pytest
from hypothesis import given

from otto.lib.weather_client import WeatherClient


@pytest.fixture(scope="session")
def mock_weather_client() -> Iterable[WeatherClient]:
    """Define the weather client to be used for the test."""
    headers = {"Content-Type": "application/json"}
    forecast_data = {"properties": {"forecast": "https://api.weather.gov/gridpoints/CLE/93,54/forecast"}}
    weather_data = {
        "properties": {
            "periods": [
                {
                    "startTime": "2023-01-01T06:00:00-00:00",
                    "endTime": "2023-12-31T23:59:59-00:00",
                    "temperature": 77,
                    "temperatureUnit": "F",
                    "windSpeed": "12 mph",
                    "windDirection": "NW",
                    "shortForecast": "Showers And Thunderstorms Likely",
                },
                {
                    "startTime": "2022-01-01T00:00:00-00:00",
                    "endTime": "2022-12-31T23:59:59-00:00",
                },
            ],
        },
    }

    with pook.use(network=True):
        pook.get(
            pook.regex("https://api.weather.gov/points/.*"),
            reply=200,
            response_type="json",
            response_headers=headers,
            response_json=forecast_data,
        )
        pook.get(
            pook.regex("https://api.weather.gov/gridpoints/.*"),
            reply=200,
            response_type="json",
            response_headers=headers,
            response_json=weather_data,
        )

        yield WeatherClient()


@pytest.fixture(scope="session")
def mock_weather_client_with_500() -> Iterable[WeatherClient]:
    """Define the weather client to be used for the test."""
    headers = {"Content-Type": "application/json"}
    forecast_data = {}
    weather_data = {}

    with pook.use(network=True):
        pook.get(
            pook.regex("https://api.weather.gov/points/.*"),
            reply=500,
            response_type="json",
            response_headers=headers,
            response_json=forecast_data,
        )
        pook.get(
            pook.regex("https://api.weather.gov/gridpoints/.*"),
            reply=500,
            response_type="json",
            response_headers=headers,
            response_json=weather_data,
        )

        yield WeatherClient()
