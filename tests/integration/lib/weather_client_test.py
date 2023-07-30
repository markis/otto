from datetime import UTC, datetime

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from otto.lib.weather_client import WeatherClient
from otto.models.team import ABBR_TO_LOCATION


@pytest.mark.asyncio()
@settings(deadline=None)
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
        assert weather.temperature
        assert weather.forecast
        assert weather.wind_direction
        assert weather.wind_speed


@pytest.mark.asyncio()
@pytest.mark.parametrize(("lat", "long"), ABBR_TO_LOCATION.values())
async def test_get_weather_at_stadiums(lat: float, long: float) -> None:
    """Test the weather client."""
    weather_client = WeatherClient()
    weather = await weather_client.get_weather(lat, long)
    assert weather
    assert weather.temperature
    assert weather.forecast
    assert weather.wind_direction
    assert weather.wind_speed
