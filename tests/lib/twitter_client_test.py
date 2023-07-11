from collections.abc import Iterable
from unittest.mock import AsyncMock, Mock, patch

import pytest
from playwright.async_api import Page

from otto.lib.twitter_client import (
    clean_tweet,
    get_tweet_text,
    get_tweet_url,
    text_contains_twitter_status_url,
)


@pytest.fixture()
def mock_playwright_page() -> Iterable[Mock]:
    """Mock a playwright page."""
    page = Mock(spec=Page)
    with patch("otto.lib.twitter_client.async_playwright") as playwright_mock:
        playwright_instance_mock = playwright_mock.return_value.__aenter__.return_value
        playwright_instance_mock.firefox.launch.return_value.new_context.return_value.new_page.return_value = page
        yield page


def test_text_contains_twitter_status_url() -> None:
    """Test the normal case for text_contains_twitter_status_url."""
    assert text_contains_twitter_status_url("Check out this tweet: https://twitter.com/user/status/123456") == (
        True,
        123456,
        "user",
    )
    assert text_contains_twitter_status_url("This is not a tweet") == (False, None, None)


@pytest.mark.parametrize(
    ("status_id", "author", "result"),
    [
        (0, "user", "https://twitter.com/user/status/0"),
        (789, "anotheruser", "https://twitter.com/anotheruser/status/789"),
        (123456, "user", "https://twitter.com/user/status/123456"),
    ],
)
def test_get_tweet_url(status_id: int, author: str, result: str) -> None:
    """Test the normal case for get_tweet_url."""
    assert get_tweet_url(status_id, author) == result


@pytest.mark.parametrize(
    ("original", "clean"),
    [
        ("This is a tweet", "This is a tweet"),
        ("This\nis\na\ntweet", "This is a tweet"),
        ("This  is  a  tweet", "This is a tweet"),
    ],
)
def test_clean_tweet(original: str, clean: str) -> None:
    """Test the normal case for clean_tweet."""
    assert clean_tweet(original) == clean


@pytest.mark.asyncio()
async def test_get_tweet_text(mock_playwright_page: Mock) -> None:
    """Test the normal case for get_tweet_text."""
    mock_playwright_page.goto.return_value = None
    mock_playwright_page.wait_for_selector.return_value = None
    mock_playwright_page.get_by_test_id.return_value = mock_element = Mock(
        spec=Page,
        first=Mock(text_content=AsyncMock(return_value="")),
    )
    mock_element.first.text_content.return_value = "This is a tweet text"

    tweet_text = await get_tweet_text(123456, "user")
    assert tweet_text == "This is a tweet text"

    mock_playwright_page.goto.assert_called_once_with("https://twitter.com/user/status/123456")
    mock_playwright_page.wait_for_selector.assert_called_once_with("article")
    mock_playwright_page.get_by_test_id.assert_called_once_with("tweetText")
    mock_element.first.text_content.assert_called_once_with()
