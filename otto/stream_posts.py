import asyncio
import datetime
from typing import TYPE_CHECKING, Final

from otto import get_reddit
from otto import logger as root_logger
from otto.config import get_config
from otto.constants import SUBREDDIT_NAME
from otto.lib.check_posts import check_post

if TYPE_CHECKING:
    from asyncpraw.models.reddit.subreddit import Subreddit

logger: Final = root_logger.getChild("stream_posts")


def run() -> None:
    """Run the main loop."""
    asyncio.run(stream_posts())


async def stream_posts() -> None:
    """Stream posts from the subreddit."""
    while True:
        async with get_reddit() as reddit:
            config = await get_config(reddit, SUBREDDIT_NAME)
            logger.info("Streaming posts: %s", datetime.datetime.now(tz=datetime.UTC))

            sr: Subreddit = await reddit.subreddit(SUBREDDIT_NAME)
            async for post in sr.stream.submissions(skip_existing=True):
                await check_post(config, post)


if __name__ == "__main__":
    run()
