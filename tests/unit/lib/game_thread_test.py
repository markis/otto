from datetime import UTC, datetime
from unittest.mock import Mock, patch

import pytest

from otto.lib.weather_client import WeatherClient
from otto.models.game import Game
from tests.factories.game import GameFactory
from tests.fixtures.weather_client import mock_weather_client


@pytest.fixture(scope="session")
def mock_get_time() -> Mock:
    """Mock the get_time function."""
    return Mock(return_value=datetime(2023, 1, 1, tzinfo=UTC))


@pytest.fixture(scope="session")
def mock_games() -> list[Game]:
    """Mock the get_time function."""
    return [GameFactory.create() for _ in range(17)]


@pytest.mark.asyncio()
@pytest.mark.usefixtures(mock_weather_client.__name__)
async def test_generate_game_thread(
    mock_nfl_client: Mock,
    mock_weather_client: WeatherClient,
    mock_get_time: Mock,
    mock_games: list[Game],
) -> None:
    """Test the generate_game_thread function."""
    mock_nfl_client().get_scores.return_value = mock_games

    with (
        patch("otto.lib.game_thread.NFLClient", mock_nfl_client),
        patch("otto.lib.game_thread.WeatherClient", mock_weather_client),
        patch("otto.lib.game_thread.get_time", mock_get_time),
    ):
        from otto.lib.game_thread import generate_game_thread

        assert await generate_game_thread()
