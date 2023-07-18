from __future__ import annotations

import logging
import sys
from typing import Final, Self

from asyncpraw.reddit import Reddit

from otto.constants import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_PASSWORD, REDDIT_USERNAME

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger: Final = logging.getLogger(__name__)


class AsyncGenReddit:
    """A context manager for AsyncPRAW."""

    _reddit: Reddit

    def __init__(self: Self, reddit: Reddit) -> None:
        """Initialize AsyncGenReddit."""
        self._reddit = reddit

    def __call__(self: Self) -> AsyncGenReddit:
        """Call the AsyncPRAW instance."""
        return self

    async def __aenter__(self: Self) -> Reddit:
        """Generate the AsyncPRAW instance."""
        return self._reddit

    async def __aexit__(self: Self, *_: object) -> None:
        """Close the AsyncPRAW instance."""
        await self._reddit.close()


def get_reddit() -> AsyncGenReddit:
    """Get the Async PRAW Reddit instance."""
    reddit = Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        username=REDDIT_USERNAME,
        password=REDDIT_PASSWORD,
        user_agent="Otto by /u/markis",
    )
    return AsyncGenReddit(reddit)
