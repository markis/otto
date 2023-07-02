from dataclasses import dataclass
from datetime import timedelta
from typing import Final

from praw import Reddit
from yaml import Loader, load

OTTO_CONFIG_PATH: Final = "ottograhaminator"


@dataclass
class Config:
    enable_automatic_sidebar_scores: bool
    enable_automatic_downvotes: bool
    downvotes_delay: timedelta
    rule7_levenshtein_threshold: int

    @classmethod
    def from_dict(cls, config: dict[str, str | int | bool | None]) -> "Config":
        enable_automatic_sidebar_scores = _convert_to_bool(config.get("enable_automatic_sidebar_scores"))
        enable_automatic_downvotes = _convert_to_bool(config.get("enable_automatic_downvotes"))
        downvotes_delay = _convert_to_timedelta(config.get("delay_downvotes", "-24hr"))
        rule7_levenshtein_threshold = _convert_to_int(config.get("rule7_levenshtein_threshold", "75"))
        return cls(
            enable_automatic_downvotes=enable_automatic_downvotes,
            enable_automatic_sidebar_scores=enable_automatic_sidebar_scores,
            downvotes_delay=downvotes_delay,
            rule7_levenshtein_threshold=rule7_levenshtein_threshold,
        )


def _convert_to_bool(val: str | int | bool | None) -> bool:
    return val in (1, True) or (type(val) == str and val.lower() in ("true", "yes", "1"))


def _convert_to_int(val: str | int | bool | None) -> int:
    if type(val) == int:
        return val
    elif type(val) == str:
        return int(val)
    elif type(val) == bool and val is True:
        return 1
    return 0


def _convert_to_timedelta(val: str | int | bool | None) -> timedelta:
    if type(val) == int:
        return timedelta(seconds=val)
    elif type(val) == str:
        from pytimeparse.timeparse import timeparse

        val_time = timeparse(val)
        assert val_time
        return timedelta(seconds=val_time)
    elif type(val) == bool and val is True:
        return timedelta(seconds=1)
    return timedelta(seconds=0)


def get_config(reddit: Reddit, subreddit_name: str) -> Config:
    sr = reddit.subreddit(subreddit_name)
    wiki_page = sr.wiki[OTTO_CONFIG_PATH]
    config_doc = wiki_page.content_md
    config_values = load(config_doc, Loader=Loader)
    return Config.from_dict(config_values)
