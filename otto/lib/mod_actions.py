import logging

from typing import Callable
from typing import Coroutine
from typing import Optional

from praw import Reddit
from praw.exceptions import APIException

from otto.typing import SendMessage

logger = logging.getLogger(__name__)


def is_mod(reddit: Reddit, sr_name: str, user_name: str) -> bool:
    sr = reddit.subreddit(sr_name)
    rel = sr.moderator(user_name)
    return len(rel.children) > 0


def get_rule(reddit: Reddit, sr_name: str, rule_num: int) -> str:
    sr = reddit.subreddit(sr_name)
    rules = sr.rules()["rules"]
    rule_short_name = rules[rule_num - 1]["short_name"]
    assert isinstance(rule_short_name, str)
    return rule_short_name


def ban_user(
    reddit: Reddit,
    sr_name: str,
    send_message: Callable[[str], None],
    mod_name: str,
    user_name: str,
    rule_violation: Optional[int],
    duration: Optional[int],
    ban_message: Optional[str],
    note: Optional[str],
) -> None:
    if user_name.startswith("u/"):
        user_name = user_name[2:]

    logger.info(f"{mod_name} banned {user_name}")
    sr = reddit.subreddit(sr_name)

    ban_reason = ""
    if rule_violation and rule_violation > 0:
        ban_reason = get_rule(reddit, sr_name, rule_violation)

    try:
        sr.banned.add(
            user_name,
            ban_reason=ban_reason,
            ban_message=ban_message,
            duration=duration,
            note=note,
        )
    except APIException as e:
        send_message(f"Ban failed because: {e.message}")
        return

    ban_duration = "permanently"
    if duration:
        ban_duration = f"for {duration} days"

    send_message(
        f'u/{user_name} has been banned {ban_duration} for violating "{ban_reason}"'
    )


def set_link_type(reddit: Reddit, sr_name: str, link_type: str) -> str:
    assert reddit
    assert sr_name
    assert link_type in ["any", "link", "self"]

    sr = reddit.subreddit(sr_name)
    sr.mod.update(link_type=link_type)

    responses = {
        "any": "All post types are enabled",
        "link": "Text posts are disabled",
        "self": "Only text posts are enabled",
    }
    return responses[link_type]


async def enable_text_posts(
    reddit: Reddit, sr_name: str, send_message: SendMessage
) -> None:
    result = set_link_type(reddit, sr_name, "any")
    await send_message(result)


async def disable_text_posts(
    reddit: Reddit, sr_name: str, send_message: SendMessage
) -> None:
    result = set_link_type(reddit, sr_name, "link")
    await send_message(result)
