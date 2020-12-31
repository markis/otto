from dataclasses import dataclass
from datetime import timedelta
from typing import Dict

from praw import Reddit
from yaml import load
from yaml import Loader


OTTO_CONFIG_PATH = "ottograhaminator"


@dataclass
class Config(object):
    enable_automatic_sidebar_scores: bool
    enable_automatic_downvotes: bool
    downvotes_delay: timedelta

    rule7_levenshtein_threshold: int

    @classmethod
    def from_dict(cls, config: Dict[str, str]) -> "Config":
        enable_automatic_sidebar_scores = bool(
            config.get("enable_automatic_sidebar_scores")
        )

        enable_automatic_downvotes = bool(config.get("enable_automatic_downvotes"))

        from pytimeparse.timeparse import timeparse

        delay_downvotes_sval = config.get("delay_downvotes", "24hr")
        downvotes_delay = timedelta(seconds=timeparse(delay_downvotes_sval))

        rule7_levenshtein_threshold = int(
            config.get("rule7_levenshtein_threshold", "75")
        )
        return cls(
            enable_automatic_downvotes=enable_automatic_downvotes,
            enable_automatic_sidebar_scores=enable_automatic_sidebar_scores,
            downvotes_delay=downvotes_delay,
            rule7_levenshtein_threshold=rule7_levenshtein_threshold,
        )


def get_config(reddit: Reddit, subreddit_name: str) -> Config:
    sr = reddit.subreddit(subreddit_name)
    wiki_page = sr.wiki[OTTO_CONFIG_PATH]
    config_doc = wiki_page.content_md
    config_values = load(config_doc, Loader=Loader)
    return Config.from_dict(config_values)
