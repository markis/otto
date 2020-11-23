import datetime
import logging
import threading

from typing import Type

from praw import Reddit

from otto import get_reddit
from otto import SUBREDDIT_NAME
from otto.config import get_config
from otto.lib.nfl_client import NFLClient
from otto.lib.update_downvote import update_downvote
from otto.lib.update_sidebar_score import update_sidebar_score
from otto.models.game import Game


logger = logging.getLogger(__name__)


def run_jobs(
    reddit: Reddit = get_reddit(), timer: Type[threading.Timer] = threading.Timer
) -> None:
    timer(300, run_jobs).start()
    logger.info("Running Jobs: {}".format(datetime.datetime.now()))
    sr_name = SUBREDDIT_NAME
    config = get_config(reddit, sr_name)
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


if __name__ == "__main__":
    run_jobs()
