import logging
import sys
from typing import Final, Self

from asyncpraw.reddit import Reddit

from otto.constants import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_PASSWORD, REDDIT_USERNAME

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger: Final = logging.getLogger(__name__)


class AsyncGenReddit:
    """A context manager for AsyncPRAW."""

    def __init__(self: Self) -> None:
        """Initialize AsyncGenReddit."""
        self.reddit = Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            username=REDDIT_USERNAME,
            password=REDDIT_PASSWORD,
            user_agent="Otto by /u/markis",
        )

    async def __aenter__(self: Self) -> Reddit:
        """Generate the AsyncPRAW instance."""
        return self.reddit

    async def __aexit__(self: Self, *_: object) -> None:
        """Close the AsyncPRAW instance."""
        await self.reddit.close()


def get_reddit() -> AsyncGenReddit:
    """Get the Async PRAW Reddit instance."""
    return AsyncGenReddit()
