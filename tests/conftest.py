import glob
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, Mock

import pytest
from asyncpraw.models.reddit.subreddit import Subreddit, SubredditWiki
from asyncpraw.models.reddit.wikipage import WikiPage
from asyncpraw.reddit import Reddit

from otto import AsyncGenReddit
from otto.config import Config

for file in glob.glob("tests/fixtures/*.py"):
    module = file.replace("/", ".")[:-3]
    print(module)
    __import__(module, locals(), globals(), ("*",))


@pytest.fixture(scope="module")
def mock_reddit() -> Mock:
    """Mock the Reddit class."""
    wiki_page = AsyncMock(spec=WikiPage, content_md="")
    subreddit_wiki = AsyncMock(spec=SubredditWiki, get_page=AsyncMock(spec=SubredditWiki, return_value=wiki_page))
    subreddit = AsyncMock(spec=Subreddit, return_value=AsyncMock(spec=Subreddit, wiki=subreddit_wiki))
    return Mock(
        spec=Reddit,
        subreddit=subreddit,
    )


@pytest.fixture(scope="module")
def mock_get_reddit(mock_reddit: AsyncMock) -> AsyncGenReddit:
    """Mock the get_reddit function."""
    return AsyncGenReddit(mock_reddit)


@pytest.fixture(scope="module")
def mock_config() -> Mock:
    """Mock the Config class."""
    return Mock(spec=Config)


@pytest.fixture(scope="module")
def mock_get_config(mock_config: Mock) -> AsyncMock:
    """Mock the get_config function."""
    return AsyncMock(return_value=mock_config)


@pytest.fixture(scope="module")
def mock_nfl_client() -> Mock:
    """Mock the NFLClient."""
    from otto.lib.nfl_client import NFLClient

    if TYPE_CHECKING:
        from otto.models.game import Game
        from otto.models.record import Record

    mock_nfl_client = Mock(spec=NFLClient)
    games: list[Game] = []
    records: list[Record] = []
    mock_nfl_client().get_scores.return_value = games
    mock_nfl_client().get_standings.return_value = records
    return mock_nfl_client
