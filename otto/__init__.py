import inspect
import logging
import os
import sys
from typing import Final

from praw import Reddit

TEAM_NAME: Final = os.environ.get("TEAM_NAME", "CLE")
SUBREDDIT_NAME: Final = os.environ.get("SUBREDDIT_NAME", "Browns")
REDDIT_CLIENT_ID: Final = os.environ.get("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET: Final = os.environ.get("REDDIT_CLIENT_SECRET")
REDDIT_USERNAME: Final = os.environ.get("REDDIT_USERNAME")
REDDIT_PASSWORD: Final = os.environ.get("REDDIT_PASSWORD")
DISCORD_BOT_ID: Final = os.environ.get("DISCORD_BOT_ID")
DISCORD_GUILD_ID: Final = os.environ.get("DISCORD_GUILD_ID")
DISCORD_TOKEN: Final = os.environ.get("DISCORD_TOKEN")
TWITTER_KEY: Final = os.environ.get("TWITTER_KEY")
TWITTER_SECRET: Final = os.environ.get("TWITTER_SECRET")

try:
    MODULE_DIRECTORY = os.path.dirname(__file__)
    ASSETS_DIRECTORY = os.path.normpath(MODULE_DIRECTORY + "/../assets")
except KeyError:
    stack = inspect.stack()
    __file__ = stack[1].filename
    MODULE_DIRECTORY = os.path.dirname(__file__)
    ASSETS_DIRECTORY = os.path.normpath(MODULE_DIRECTORY + "/../assets")

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


_reddit = Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    username=REDDIT_USERNAME,
    password=REDDIT_PASSWORD,
    user_agent="Otto by /u/markis",
)


def get_reddit() -> Reddit:
    global _reddit
    return _reddit
