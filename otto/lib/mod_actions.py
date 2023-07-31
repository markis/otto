import logging
from typing import Final

from asyncpraw.reddit import Reddit

logger: Final = logging.getLogger(__name__)


async def set_link_type(reddit: Reddit, sr_name: str, link_type: str) -> str:
    """Set the link type for a subreddit."""
    assert reddit
    assert sr_name
    assert link_type in ["any", "link", "self"]

    sr = await reddit.subreddit(sr_name)
    sr.mod.update(link_type=link_type)

    responses = {
        "any": "All post types are enabled",
        "link": "Text posts are disabled",
        "self": "Only text posts are enabled",
    }
    return responses[link_type]


async def enable_text_posts(reddit: Reddit, sr_name: str) -> str:
    """Enable text posts for a subreddit."""
    return await set_link_type(reddit, sr_name, "any")


async def disable_text_posts(reddit: Reddit, sr_name: str) -> str:
    """Disable text posts for a subreddit."""
    return await set_link_type(reddit, sr_name, "link")
