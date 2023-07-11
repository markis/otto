from unittest.mock import AsyncMock, Mock

import pytest
from asyncpraw.models.reddit.subreddit import Subreddit, SubredditWiki
from asyncpraw.models.reddit.wikipage import WikiPage
from asyncpraw.reddit import Reddit


@pytest.fixture()
def mock_reddit() -> Mock:
    """Mock the Reddit class."""
    wiki_page = AsyncMock(spec=WikiPage, content_md="")
    subreddit_wiki = AsyncMock(spec=SubredditWiki, get_page=AsyncMock(spec=SubredditWiki, return_value=wiki_page))
    subreddit = AsyncMock(spec=Subreddit, return_value=AsyncMock(spec=Subreddit, wiki=subreddit_wiki))
    return Mock(
        spec=Reddit,
        subreddit=subreddit,
    )
