import logging
from typing import Final

from fuzzywuzzy import fuzz
from praw.models import Submission

from otto.config import Config
from otto.lib.twitter_client import get_status, get_status_id, get_tweet_from_status

logger: Final = logging.getLogger(__name__)


def check_post(config: Config, post: Submission) -> None:
    """
    Check a post that it is not sensationalized based on the title of the source tweet.
    """
    logger.info(f"Checking post: {post.id}")
    if post.approved_by:
        logger.info(f"Post already approved: {post.approved_by}")
        return

    post_title = post.title
    source_title = None

    twitter_status_id = get_status_id(post.url)
    if twitter_status_id:
        twitter_status = get_status(twitter_status_id)
        source_title = get_tweet_from_status(twitter_status)

    if source_title and post_title:
        partial_ratio = fuzz.partial_ratio(source_title, post_title)
        diag_comment = post.reply(_get_diagnostic_comment(config, source_title, post_title, partial_ratio))
        assert diag_comment
        diag_comment.mod.remove()
        if partial_ratio < config.rule7_levenshtein_threshold:
            post.mod.flair("Rule7")
            post.report("No Sensationalized Titles")
            print(f"Post removed for Rule 7: {post.id}")


def _get_diagnostic_comment(config: Config, source_title: str, post_title: str, levenshtein_distance: int) -> str:
    return f"""
Diagnostics:

Source Title: "{source_title}"

Reddit Title: "{post_title}"

Levenshtein Distance: {levenshtein_distance}/{config.rule7_levenshtein_threshold}
"""
