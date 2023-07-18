from datetime import UTC, datetime
from unittest.mock import Mock, patch

import pytest

from otto.lib.weather_client import WeatherClient
from otto.models.game import Game
from tests.factories.game import GameFactory


@pytest.fixture(scope="session")
def mock_weather_client() -> Mock:
    """Mock the WeatherClient."""
    return Mock(spec=WeatherClient, get_weather=Mock(return_value=""))


@pytest.fixture(scope="session")
def mock_get_time() -> Mock:
    """Mock the get_time function."""
    return Mock(return_value=datetime(2023, 1, 1, tzinfo=UTC))


@pytest.fixture(scope="session")
def mock_games() -> list[Game]:
    """Mock the get_time function."""
    return [GameFactory.create() for _ in range(17)]


@pytest.mark.asyncio()
async def test_generate_game_thread(
    mock_nfl_client: Mock,
    mock_weather_client: Mock,
    mock_get_time: Mock,
    mock_games: list[Game],
) -> None:
    """Test the generate_game_thread function."""
    mock_nfl_client().get_scores.return_value = mock_games
    mock_weather_client().get_weather.return_value = ""

    with (
        patch("otto.lib.game_thread.NFLClient", mock_nfl_client),
        patch("otto.lib.game_thread.WeatherClient", mock_weather_client),
        patch("otto.lib.game_thread.get_time", mock_get_time),
    ):
        from otto.lib.game_thread import generate_game_thread

        assert await generate_game_thread()
