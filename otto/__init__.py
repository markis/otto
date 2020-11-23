import logging
import os
import sys

from flask import Flask
from praw import Reddit

TEAM_NAME = os.environ.get("TEAM_NAME", "CLE")
SUBREDDIT_NAME = os.environ.get("SUBREDDIT_NAME", "Browns")
REDDIT_CLIENT_ID = os.environ.get("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET = os.environ.get("REDDIT_CLIENT_SECRET")
REDDIT_USERNAME = os.environ.get("REDDIT_USERNAME")
REDDIT_PASSWORD = os.environ.get("REDDIT_PASSWORD")

MODULE_DIRECTORY = os.path.dirname(__file__)
ASSETS_DIRECTORY = os.path.normpath(MODULE_DIRECTORY + "/../assets")
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


_reddit = None


def get_reddit() -> Reddit:
    global _reddit
    if not _reddit:
        _reddit = Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            username=REDDIT_USERNAME,
            password=REDDIT_PASSWORD,
            user_agent="Otto by /u/markis",
        )
    return _reddit
