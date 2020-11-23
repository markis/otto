from datetime import timedelta
from typing import Dict

from praw import Reddit
from yaml import dump
from yaml import Dumper
from yaml import load
from yaml import Loader


OTTO_CONFIG_PATH = "ottograhaminator"


class Config(object):
    enable_automatic_sidebar_scores: bool
    enable_automatic_downvotes: bool
    downvotes_delay: timedelta

    def __init__(self, config: Dict[str, str]):
        self.enable_automatic_sidebar_scores = bool(
            config.get("enable_automatic_sidebar_scores")
        )

        self.enable_automatic_downvotes = bool(config.get("enable_automatic_downvotes"))

        from pytimeparse.timeparse import timeparse

        delay_downvotes_sval = config.get("delay_downvotes", "24hr")
        self.downvotes_delay = timedelta(seconds=timeparse(delay_downvotes_sval))


def get_config(reddit: Reddit, subreddit_name: str) -> Config:
    sr = reddit.subreddit(subreddit_name)
    wiki_page = sr.wiki[OTTO_CONFIG_PATH]
    config_doc = wiki_page.content_md
    config_values = load(config_doc, Loader=Loader)
    return Config(config_values)
