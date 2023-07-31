import re
from datetime import UTC, datetime, timedelta
from typing import Final

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from otto.constants import DEFAULT_TIMEOUT
from otto.lib.weather_client import WeatherClient
from otto.models.team import ABBR_TO_LOCATION

LOWEST_TEMP: Final = -50
HIGHEST_TEMP: Final = 150
WIND_SPEED_PATTERN: Final = r"\d+(\sto\s\d+)?\s(mph|km/h)"
WIND_DIRECTION: Final = r"(N|NNE|NE|ENE|E|ESE|SE|SSE|S|SSW|SW|WSW|W|WNW|NW|NNW)"


@pytest.mark.functional()
@pytest.mark.asyncio()
@settings(deadline=timedelta(seconds=DEFAULT_TIMEOUT))
@given(
    lat=st.floats(min_value=24.396308, max_value=49.384358),  # max and min values for the USA
    long=st.floats(min_value=-124.848974, max_value=-66.885444),  # max and min values for the USA
    date=st.one_of(st.none(), st.datetimes(timezones=st.just(UTC))),
)
async def test_fuzz_get_weather(lat: float, long: float, date: datetime | None) -> None:
    """Test the weather client."""
    weather_client = WeatherClient()
    weather = await weather_client.get_weather(lat=lat, long=long, date=date)

    if weather:
        assert LOWEST_TEMP < weather.temperature < HIGHEST_TEMP
        assert re.match(WIND_DIRECTION, weather.wind_direction)
        assert re.match(WIND_SPEED_PATTERN, weather.wind_speed)
        assert weather.forecast


@pytest.mark.integration()
@pytest.mark.vcr()
@pytest.mark.block_network()
@pytest.mark.asyncio()
@pytest.mark.parametrize(("lat", "long"), ABBR_TO_LOCATION.values())
async def test_get_weather_at_stadiums(lat: float, long: float) -> None:
    """Test the weather client."""
    # if you record new outputs for this test, then you will need update this date
    test_date: Final = datetime(2023, 7, 31, 12, tzinfo=UTC)

    weather_client = WeatherClient()
    weather = await weather_client.get_weather(lat, long, test_date)
    assert weather
    assert LOWEST_TEMP < weather.temperature < HIGHEST_TEMP
    assert re.match(WIND_DIRECTION, weather.wind_direction)
    assert re.match(WIND_SPEED_PATTERN, weather.wind_speed)
    assert weather.forecast
