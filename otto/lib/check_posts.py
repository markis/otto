import logging

from fuzzywuzzy import fuzz
from praw.models import Submission

from otto.lib.twitter_client import get_status
from otto.lib.twitter_client import get_status_id
from otto.lib.twitter_client import get_tweet_from_status


logger = logging.getLogger(__name__)


async def check_post(post: Submission) -> None:
    if post.approved_by:
        return

    twitter_status_id = get_status_id(post.url)
    if twitter_status_id:
        twitter_status = get_status(twitter_status_id)
        tweet = get_tweet_from_status(twitter_status)
        post_title = post.title

        partial_ratio = fuzz.partial_ratio(tweet, post_title)
        if partial_ratio < 75:
            post.mod.flair("Rule7")
            post.report("No Sensationalized Titles")
            logger.info(f"{post.name}, {post.url}")
