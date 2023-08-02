import re
from datetime import UTC, datetime, timedelta
from typing import Final

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from otto.constants import DEFAULT_TIMEOUT
from otto.lib.weather_client import WeatherClient
from otto.models.team import ABBR_TO_LOCATION
from tests.fixtures.weather_client import mock_weather_client, mock_weather_client_with_500

LATITUDE: Final = 41.506160
LONGITUDE: Final = -81.699580
DATE: Final = datetime(2023, 9, 1, tzinfo=UTC)
LOWEST_TEMP: Final = -50
HIGHEST_TEMP: Final = 150
WIND_SPEED_PATTERN: Final = r"\d+(\sto\s\d+)?\s(mph|km/h)"
WIND_DIRECTION: Final = r"(N|NNE|NE|ENE|E|ESE|SE|SSE|S|SSW|SW|WSW|W|WNW|NW|NNW)"


@pytest.mark.unit()
@pytest.mark.asyncio()
@pytest.mark.usefixtures(mock_weather_client.__name__)
async def test_weather_client(mock_weather_client: WeatherClient) -> None:
    """Test the weather client with a mocked client."""
    expected_temperature = 77

    assert (weather := await mock_weather_client.get_weather(LATITUDE, LONGITUDE, DATE))
    assert weather.temperature == expected_temperature
    assert weather.wind_speed == "12 mph"
    assert weather.wind_direction == "NW"
    assert weather.forecast == "Showers And Thunderstorms Likely"


@pytest.mark.unit()
@pytest.mark.asyncio()
@pytest.mark.usefixtures(mock_weather_client_with_500.__name__)
async def test_bad_weather_client(mock_weather_client_with_500: WeatherClient) -> None:
    """Test the weather client mocked 500 client."""
    weather = await mock_weather_client_with_500.get_weather(LATITUDE, LONGITUDE, DATE)
    assert weather is None


@pytest.mark.block_network()
@pytest.mark.integration()
@pytest.mark.vcr()
@pytest.mark.asyncio()
@pytest.mark.parametrize(("team_abbr", "location"), ABBR_TO_LOCATION.items())
async def test_get_weather_at_stadiums(team_abbr: str, location: tuple[float, float]) -> None:
    """Test the weather client."""
    # if you record new outputs for this test, then you will need update this date
    test_date: Final = datetime(2023, 8, 1, 12, tzinfo=UTC)
    lat, long = location
    del team_abbr

    weather_client = WeatherClient()
    weather = await weather_client.get_weather(lat, long, test_date)
    assert weather
    assert LOWEST_TEMP < weather.temperature < HIGHEST_TEMP
    assert re.match(WIND_DIRECTION, weather.wind_direction)
    assert re.match(WIND_SPEED_PATTERN, weather.wind_speed)
    assert weather.forecast


@pytest.mark.functional()
@pytest.mark.asyncio()
@settings(deadline=timedelta(seconds=DEFAULT_TIMEOUT))
@given(
    lat=st.floats(min_value=24.7433195, max_value=49.3457868),  # max and min values for the USA
    long=st.floats(min_value=-124.7844079, max_value=-66.9513812),  # max and min values for the USA
    date=st.one_of(st.none(), st.datetimes(timezones=st.just(UTC))),
)
async def test_fuzzy_get_weather(lat: float, long: float, date: datetime | None) -> None:
    """Test the weather client."""
    weather_client = WeatherClient()
    weather = await weather_client.get_weather(lat=lat, long=long, date=date)

    if weather:
        assert LOWEST_TEMP < weather.temperature < HIGHEST_TEMP
        assert re.match(WIND_DIRECTION, weather.wind_direction)
        assert re.match(WIND_SPEED_PATTERN, weather.wind_speed)
        assert weather.forecast
