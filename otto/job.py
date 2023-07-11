import asyncio
import datetime
from typing import Final

from asyncpraw.reddit import Reddit

from otto import get_reddit
from otto import logger as root_logger
from otto.config import Config, get_config
from otto.constants import SUBREDDIT_NAME
from otto.lib.nfl_client import NFLClient
from otto.lib.update_downvote import update_downvote
from otto.lib.update_sidebar_score import update_sidebar_score
from otto.utils import repeat

logger: Final = root_logger.getChild("job")


def run() -> None:
    """Run the jobs. This is the entry point for the job. It's main point is convert async to sync."""
    asyncio.run(main())


async def main(sr_name: str = SUBREDDIT_NAME) -> None:
    """Run jobs every 5 minutes."""
    async with get_reddit() as reddit:
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
    """Run all jobs."""
    logger.info("Running Jobs: %s", datetime.datetime.now(tz=datetime.UTC))
    client = NFLClient()
    games = client.get_scores()
    records = client.get_standings()

    if config.enable_automatic_sidebar_scores:
        try:
            await update_sidebar_score(reddit, sr_name, games, records)
        except Exception:
            logger.exception("Error updating sidebar score")

    if config.enable_automatic_downvotes:
        try:
            await update_downvote(config, reddit, sr_name, games)
        except Exception:
            logger.exception("Error updating downvotes")


if __name__ == "__main__":
    run()
