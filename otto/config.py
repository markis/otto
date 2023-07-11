from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, Self, final

from asyncpraw.models.reddit.subreddit import Subreddit, SubredditWiki
from yaml import safe_load

from otto.utils.convert import convert_to_bool, convert_to_int, convert_to_timedelta

if TYPE_CHECKING:  # pragma: no cover
    from datetime import timedelta

    from asyncpraw.models.reddit.wikipage import WikiPage
    from asyncpraw.reddit import Reddit

OTTO_CONFIG_PATH: Final = "ottograhaminator"


@dataclass(init=False)
@final
class Config:
    """Config for OttoGrahaminator."""

    enable_automatic_sidebar_scores: Final[bool]
    enable_automatic_downvotes: Final[bool]
    downvotes_delay: Final[timedelta]
    rule7_levenshtein_threshold: Final[int]

    def __init__(
        self: Self,
        *,
        enable_automatic_sidebar_scores: bool,
        enable_automatic_downvotes: bool,
        downvotes_delay: timedelta,
        rule7_levenshtein_threshold: int,
    ) -> None:
        """Initialize a Config object."""
        self.enable_automatic_sidebar_scores = enable_automatic_sidebar_scores
        self.enable_automatic_downvotes = enable_automatic_downvotes
        self.downvotes_delay = downvotes_delay
        self.rule7_levenshtein_threshold = rule7_levenshtein_threshold

    @classmethod
    def from_toml(cls: type[Config], config: str) -> Config:
        """Create a Config object from a yaml string."""
        config_values = safe_load(config) or {}
        return cls.from_dict(config_values)

    @classmethod
    def from_yaml(cls: type[Config], config: str) -> Config:
        """Create a Config object from a yaml string."""
        config_values = safe_load(config) or {}
        return cls.from_dict(config_values)

    @classmethod
    def from_dict(cls: type[Config], config: dict[str, str | int | bool | None]) -> Config:
        """Create a Config object from a dictionary."""
        assert isinstance(config, dict), "Config is not a dictionary"
        enable_automatic_sidebar_scores = convert_to_bool(config.get("enable_automatic_sidebar_scores", False))
        enable_automatic_downvotes = convert_to_bool(config.get("enable_automatic_downvotes", False))
        downvotes_delay = convert_to_timedelta(config.get("delay_downvotes", "-24hr"))
        rule7_levenshtein_threshold = convert_to_int(config.get("rule7_levenshtein_threshold", "75"))
        return cls(
            enable_automatic_downvotes=enable_automatic_downvotes,
            enable_automatic_sidebar_scores=enable_automatic_sidebar_scores,
            downvotes_delay=downvotes_delay,
            rule7_levenshtein_threshold=rule7_levenshtein_threshold,
        )


async def get_config(reddit: Reddit, subreddit_name: str) -> Config:
    """Get the config from the subreddit wiki (/ottograhaminator)."""
    sr: Subreddit = await reddit.subreddit(subreddit_name)
    wiki: SubredditWiki = sr.wiki
    assert isinstance(wiki, SubredditWiki), "Wiki is not a SubredditWiki"
    wikipage: WikiPage = await wiki.get_page(OTTO_CONFIG_PATH)
    config_doc = str(wikipage.content_md)
    return Config.from_yaml(config_doc)
