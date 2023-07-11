from textwrap import dedent
from typing import Final

from asyncpraw.models import Submission
from fuzzywuzzy import fuzz

from otto import logger as root_logger
from otto.config import Config
from otto.lib.twitter_client import (
    get_tweet_text,
    text_contains_twitter_status_url,
)

logger: Final = root_logger.getChild("lib.check_posts")


async def check_post(config: Config, post: Submission) -> None:
    """Check a post that it is not sensationalized based on the title of the source tweet."""
    logger.info("Checking post: %s", post.id)
    if post.approved_by:
        logger.info("Post already approved: %s", post.approved_by)
        return

    post_title = post.title
    source_title = None

    has_tweet, status_id, author = text_contains_twitter_status_url(post.url)
    if has_tweet and status_id:
        source_title = await get_tweet_text(status_id, author) if author else await get_tweet_text(status_id)

    if source_title and post_title:
        partial_ratio = fuzz.partial_ratio(source_title, post_title)
        diag_comment = await post.reply(_get_diagnostic_comment(config, source_title, post_title, partial_ratio))
        assert diag_comment
        await diag_comment.mod.remove()
        if partial_ratio < config.rule7_levenshtein_threshold:
            await post.mod.flair("Rule7")
            await post.report("No Sensationalized Titles")
            logger.info("Post removed for Rule 7: %s", post.id)


def _get_diagnostic_comment(config: Config, source_title: str, post_title: str, levenshtein_distance: int) -> str:
    diag = f"""
        Diagnostics:

        Source Title: "{source_title}"

        Reddit Title: "{post_title}"

        Levenshtein Distance: {levenshtein_distance}/{config.rule7_levenshtein_threshold}
    """
    return dedent(diag)
