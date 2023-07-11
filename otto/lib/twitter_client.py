import html
import re
from typing import Any

from playwright.async_api import async_playwright

from otto.constants import TWITTER_AUTH_COOKIE

twitter_status_url_re = re.compile(r".*https?:\/\/(mobile.)?twitter\.com\/(?:#!\/)?(\w+)\/status(es)?\/(\d+).*")
truncated_tweet_re = re.compile(r"(.*?)(\…?\s*)https:\/\/t.co\/.*?$")

COOKIES: list[Any] = [
    {
        "name": "auth_token",
        "value": TWITTER_AUTH_COOKIE,
        "domain": ".twitter.com",
        "path": "/",
        "httpOnly": True,
        "secure": True,
    },
]


def text_contains_twitter_status_url(text: str) -> tuple[bool, int | None, str | None]:
    """Check if a string contains a Twitter status URL."""
    matches = twitter_status_url_re.search(text)
    if matches:
        return True, int(matches[4]), matches[2]
    return False, None, None


def get_tweet_url(status_id: int, author: str = "anyuser") -> str:
    """Get the URL for a tweet."""
    return f"https://twitter.com/{author}/status/{status_id}"


def clean_tweet(tweet: str) -> str:
    """Clean a tweet string."""
    return html.unescape(tweet).replace("\n", " ").replace("  ", " ")


async def get_tweet_text(status_id: int, author: str = "anyuser") -> str:
    """Get the text of a tweet."""
    async with async_playwright() as p:
        browser = await p.firefox.launch()
        context = await browser.new_context()
        await context.add_cookies(COOKIES)
        page = await context.new_page()
        await page.goto(f"https://twitter.com/{author}/status/{status_id}")
        await page.wait_for_selector("article")
        element = page.get_by_test_id("tweetText")
        assert element, "Tweet text element not found, div['data-testid=\"tweetText\"']"
        text = await element.first.text_content()
        await browser.close()
        text = clean_tweet(text) if text else ""
        return str(text)
