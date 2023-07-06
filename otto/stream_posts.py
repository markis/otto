import asyncio
import datetime
import logging
from typing import Final

from asyncpraw.models.reddit.subreddit import Subreddit

from otto import SUBREDDIT_NAME, get_reddit
from otto.config import get_config
from otto.lib.check_posts import check_post

logger: Final = logging.getLogger(__name__)


def run() -> None:
    asyncio.run(stream_posts())


async def stream_posts() -> None:
    while True:
        async with get_reddit() as reddit:
            config = await get_config(reddit, SUBREDDIT_NAME)
            logger.info(f"Streaming posts: {datetime.datetime.now()}")

            sr: Subreddit = await reddit.subreddit(SUBREDDIT_NAME)
            async for post in sr.stream.submissions(skip_existing=True):
                await check_post(config, post)


if __name__ == "__main__":
    run()
