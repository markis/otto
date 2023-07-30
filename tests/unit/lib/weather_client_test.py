from datetime import UTC, datetime
from typing import Final

import pytest

from otto.lib.weather_client import WeatherClient
from tests.fixtures.weather_client import mock_weather_client, mock_weather_client_with_500

LATITUDE: Final = 41.506160
LONGITUDE: Final = -81.699580
DATE: Final = datetime(2023, 9, 1, tzinfo=UTC)


@pytest.mark.asyncio()
@pytest.mark.usefixtures(mock_weather_client.__name__)
async def test_weather_client(mock_weather_client: WeatherClient) -> None:
    """Test the weather client."""
    expected_temperature = 77

    assert (weather := await mock_weather_client.get_weather(LATITUDE, LONGITUDE, DATE))
    assert weather.temperature == expected_temperature
    assert weather.wind_speed == "12 mph"
    assert weather.wind_direction == "NW"
    assert weather.forecast == "Showers And Thunderstorms Likely"


@pytest.mark.asyncio()
@pytest.mark.usefixtures(mock_weather_client_with_500.__name__)
async def test_bad_weather_client(mock_weather_client_with_500: WeatherClient) -> None:
    """Test the weather client."""
    weather = await mock_weather_client_with_500.get_weather(LATITUDE, LONGITUDE, DATE)
    assert weather is None
