import asyncio
import datetime
import logging
import threading

from typing import Type

from praw import Reddit

from otto import get_reddit
from otto import SUBREDDIT_NAME
from otto.config import Config
from otto.config import get_config
from otto.lib.check_posts import check_post
from otto.lib.nfl_client import NFLClient
from otto.lib.update_downvote import update_downvote
from otto.lib.update_sidebar_score import update_sidebar_score


logger = logging.getLogger(__name__)


def main(reddit: Reddit = get_reddit(), sr_name: str = SUBREDDIT_NAME) -> None:
    config = get_config(reddit, sr_name)

    run_jobs(config, reddit)
    check_submissions(config, reddit)


def run_jobs(
    config: Config,
    reddit: Reddit = get_reddit(),
    sr_name: str = SUBREDDIT_NAME,
    timer: Type[threading.Timer] = threading.Timer,
) -> None:
    timer(300, run_jobs).start()
    logger.info("Running Jobs: {}".format(datetime.datetime.now()))
    client = NFLClient()
    games = client.get_scores()
    records = client.get_standings()

    if config.enable_automatic_sidebar_scores:
        try:
            update_sidebar_score(config, reddit, sr_name, games, records)
        except Exception as e:
            logger.exception(e)

    if config.enable_automatic_downvotes:
        try:
            update_downvote(config, reddit, sr_name, games)
        except Exception as e:
            logger.exception(e)


def check_submissions(config: Config, reddit: Reddit = get_reddit()) -> None:
    logger.info("Streaming posts: {}".format(datetime.datetime.now()))

    sr = reddit.subreddit(SUBREDDIT_NAME)
    for post in sr.stream.submissions(skip_existing=True):
        asyncio.run(check_post(config, post))


if __name__ == "__main__":
    main()
