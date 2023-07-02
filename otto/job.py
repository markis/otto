import datetime
import logging
import threading

from praw import Reddit

from otto import SUBREDDIT_NAME, get_reddit
from otto.config import Config, get_config
from otto.lib.nfl_client import NFLClient
from otto.lib.update_downvote import update_downvote
from otto.lib.update_sidebar_score import update_sidebar_score

logger = logging.getLogger(__name__)


def main(reddit: Reddit = get_reddit(), sr_name: str = SUBREDDIT_NAME) -> None:
    config = get_config(reddit, sr_name)

    run_jobs(config, reddit)


def run_jobs(
    config: Config,
    reddit: Reddit = get_reddit(),
    sr_name: str = SUBREDDIT_NAME,
    timer: type[threading.Timer] = threading.Timer,
) -> None:
    def _run_jobs() -> None:
        run_jobs(config, reddit, sr_name, timer)

    timer(300, _run_jobs).start()
    logger.info(f"Running Jobs: {datetime.datetime.now()}")
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
    main()
