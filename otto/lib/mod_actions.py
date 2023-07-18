import logging
from typing import TYPE_CHECKING, Final, NamedTuple

from asyncpraw.exceptions import APIException
from asyncpraw.models.reddit.redditor import Redditor
from asyncpraw.reddit import Reddit

from otto.types import SendMessage

if TYPE_CHECKING:
    from asyncpraw.models.reddit.rules import Rule
    from asyncpraw.models.reddit.subreddit import Subreddit

logger: Final = logging.getLogger(__name__)


async def is_mod(reddit: Reddit, sr_name: str, user_name: str) -> bool:
    """Check if a user is a mod of a subreddit."""
    sr: Subreddit = await reddit.subreddit(sr_name)
    return any(mod for mod in await sr.moderator(user_name) if isinstance(mod, Redditor) and mod.name == user_name)


async def get_rule(reddit: Reddit, sr_name: str, rule_num: int) -> str:
    """Get the short name of a subreddit rule."""
    sr: Subreddit = await reddit.subreddit(sr_name)
    rule: Rule = await sr.rules.get_rule(rule_num)
    return str(rule.short_name)


class BanDetails(NamedTuple):
    """Details for banning a user."""

    mod_name: str
    user_name: str
    rule_violation: int | None
    duration: int | None
    ban_message: str | None
    note: str | None


async def ban_user(
    reddit: Reddit,
    sr_name: str,
    send_message: SendMessage,
    ban_details: BanDetails,
) -> None:
    """Ban a user from a subreddit."""
    mod_name, user_name, rule_violation, duration, ban_message, note = ban_details

    if user_name.startswith("u/"):
        user_name = user_name[2:]

    logger.info("%s banned %s from %s", mod_name, user_name, sr_name)
    sr = await reddit.subreddit(sr_name)

    ban_reason = ""
    if rule_violation and rule_violation > 0:
        ban_reason = await get_rule(reddit, sr_name, rule_violation)

    try:
        await sr.banned.add(
            user_name,
            ban_reason=ban_reason,
            ban_message=ban_message,
            duration=duration,
            note=note,
        )
    except APIException as e:
        await send_message(f"Ban failed because: {e.message}")
        return

    ban_duration = "permanently"
    if duration:
        ban_duration = f"for {duration} days"

    await send_message(f'u/{user_name} has been banned {ban_duration} for violating "{ban_reason}"')


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
