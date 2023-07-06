import inspect
import logging
import os
import sys
from typing import Any, Final

from asyncpraw.reddit import Reddit


def get_file_path() -> str:
    try:
        global __file__
        return os.path.dirname(__file__)
    except KeyError:
        stack = inspect.stack()
        __file__ = stack[1].filename
        return os.path.dirname(__file__)


TEAM_NAME: Final = os.environ.get("TEAM_NAME", "CLE")
SUBREDDIT_NAME: Final = os.environ.get("SUBREDDIT_NAME", "Browns")
REDDIT_CLIENT_ID: Final = os.environ.get("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET: Final = os.environ.get("REDDIT_CLIENT_SECRET")
REDDIT_USERNAME: Final = os.environ.get("REDDIT_USERNAME")
REDDIT_PASSWORD: Final = os.environ.get("REDDIT_PASSWORD")
DISCORD_BOT_ID: Final = os.environ.get("DISCORD_BOT_ID")
DISCORD_GUILD_ID: Final = os.environ.get("DISCORD_GUILD_ID")
DISCORD_TOKEN: Final = os.environ.get("DISCORD_TOKEN")
TWITTER_AUTH_COOKIE: Final = os.environ.get("TWITTER_AUTH_COOKIE")
TWITTER_KEY: Final = os.environ.get("TWITTER_KEY")
TWITTER_SECRET: Final = os.environ.get("TWITTER_SECRET")
TWITTER_TOKEN: Final = os.environ.get("TWITTER_TOKEN")
TWITTER_TOKEN_SECRET: Final = os.environ.get("TWITTER_TOKEN_SECRET")
MODULE_DIRECTORY: Final = get_file_path()
ASSETS_DIRECTORY: Final = os.path.normpath(MODULE_DIRECTORY + "/../assets")

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger: Final = logging.getLogger(__name__)


class OttoReddit:
    def __init__(self) -> None:
        self.reddit = Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            username=REDDIT_USERNAME,
            password=REDDIT_PASSWORD,
            user_agent="Otto by /u/markis",
        )

    async def __aenter__(self) -> Reddit:
        return self.reddit

    async def __aexit__(self, *_: Any) -> None:
        await self.reddit.close()


def get_reddit() -> OttoReddit:
    return OttoReddit()
