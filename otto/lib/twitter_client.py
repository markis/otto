import html
import re

import twitter

from otto import TWITTER_KEY, TWITTER_SECRET

twitter_status_url_re = re.compile(r"^https?:\/\/(mobile.)?twitter\.com\/(?:#!\/)?(\w+)\/status(es)?\/(\d+)")
truncated_tweet_re = re.compile(r"(.*?)(\…?\s*)https:\/\/t.co\/.*?$")


def get_status(status_id: int) -> twitter.models.Status:
    if not TWITTER_KEY or not TWITTER_SECRET:
        raise ValueError(f"TWITTER_KEY: {TWITTER_KEY}, TWITTER_SECRET: {TWITTER_SECRET}")

    api = twitter.Api(
        consumer_key=TWITTER_KEY.encode("utf8"),
        consumer_secret=TWITTER_SECRET.encode("utf8"),
        application_only_auth=True,
    )
    return api.GetStatus(status_id)


def get_status_id(url: str) -> int | None:
    match = twitter_status_url_re.match(url)
    if not match:
        return None

    return int(match[4])


def get_tweet_from_status(status: twitter.models.Status) -> str:
    tweet = html.unescape(status.text).replace("\n", " ").replace("  ", " ")
    match = truncated_tweet_re.match(tweet)
    if match:
        tweet = match[1]
    return str(tweet)
