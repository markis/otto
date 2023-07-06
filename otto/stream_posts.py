import asyncio
import datetime
import logging
from typing import Final

from asyncpraw.models.reddit.subreddit import Subreddit
from asyncpraw.reddit import Reddit

from otto import SUBREDDIT_NAME, get_reddit
from otto.config import Config, get_config
from otto.lib.check_posts import check_post

logger: Final = logging.getLogger(__name__)


async def run() -> None:
    while True:
        async with get_reddit() as reddit:
            await main(reddit=reddit, sr_name=SUBREDDIT_NAME)


async def main(reddit: Reddit, sr_name: str) -> None:
    config = await get_config(reddit, sr_name)

    await stream_posts(config, reddit)


async def stream_posts(config: Config, reddit: Reddit) -> None:
    logger.info(f"Streaming posts: {datetime.datetime.now()}")

    sr: Subreddit = await reddit.subreddit(SUBREDDIT_NAME)
    async for post in sr.stream.submissions(skip_existing=True):
        await check_post(config, post)


if __name__ == "__main__":
    asyncio.run(run())
