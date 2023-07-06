import asyncio
import datetime
import logging
from typing import Final

from asyncpraw.reddit import Reddit

from otto import SUBREDDIT_NAME, get_reddit
from otto.config import Config, get_config
from otto.lib.nfl_client import NFLClient
from otto.lib.update_downvote import update_downvote
from otto.lib.update_sidebar_score import update_sidebar_score
from otto.utils import repeat

logger: Final = logging.getLogger(__name__)


async def run() -> None:
    async with get_reddit() as reddit:
        await main(reddit, sr_name=SUBREDDIT_NAME)


async def main(reddit: Reddit, sr_name: str = SUBREDDIT_NAME) -> None:
    config = await get_config(reddit, sr_name)

    async def _run_jobs() -> None:
        async with get_reddit() as reddit:
            await run_jobs(config, reddit, sr_name)

    await repeat(300, _run_jobs)


async def run_jobs(
    config: Config,
    reddit: Reddit,
    sr_name: str,
) -> None:
    logger.info(f"Running Jobs: {datetime.datetime.now()}")
    client = NFLClient()
    games = client.get_scores()
    records = client.get_standings()

    if config.enable_automatic_sidebar_scores:
        try:
            await update_sidebar_score(config, reddit, sr_name, games, records)
        except Exception as e:
            logger.exception(e)

    if config.enable_automatic_downvotes:
        try:
            await update_downvote(config, reddit, sr_name, games)
        except Exception as e:
            logger.exception(e)


if __name__ == "__main__":
    asyncio.run(run())
