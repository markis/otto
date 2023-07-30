from datetime import UTC, datetime

import pytest

from otto.lib.weather_client import WeatherClient
from tests.fixtures.weather_client import mock_weather_client


@pytest.mark.asyncio()
@pytest.mark.usefixtures(mock_weather_client.__name__)
async def test_weather_client(mock_weather_client: WeatherClient) -> None:
    """Test the weather client."""
    lat = 41.506160
    long = -81.699580
    date = datetime(2023, 9, 1, tzinfo=UTC)

    expected_temperature = 77

    assert (weather := await mock_weather_client.get_weather(lat, long, date))
    assert weather.temperature == expected_temperature
    assert weather.wind_speed == "12 mph"
    assert weather.wind_direction == "NW"
    assert weather.forecast == "Showers And Thunderstorms Likely"
