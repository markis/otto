import datetime
import logging

from praw import Reddit

from otto import SUBREDDIT_NAME, get_reddit
from otto.config import Config, get_config
from otto.lib.check_posts import check_post

logger = logging.getLogger(__name__)


def run() -> None:
    main(reddit=get_reddit(), sr_name=SUBREDDIT_NAME)


def main(reddit: Reddit = get_reddit(), sr_name: str = SUBREDDIT_NAME) -> None:
    config = get_config(reddit, sr_name)

    stream_posts(config, reddit)


def stream_posts(config: Config, reddit: Reddit = get_reddit()) -> None:
    logger.info(f"Streaming posts: {datetime.datetime.now()}")

    sr = reddit.subreddit(SUBREDDIT_NAME)
    for post in sr.stream.submissions(skip_existing=True):
        check_post(config, post)


if __name__ == "__main__":
    run()
