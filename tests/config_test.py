from datetime import timedelta
from unittest.mock import Mock

import pytest

from otto.config import Config, get_config

TEST_LEVENSHTEIN_THRESHOLD = 75
TEST_CONFIG = f"""
      enable_automatic_sidebar_scores: no
      enable_automatic_downvotes: no
      delay_downvotes: -24hr
      rule7_levenshtein_threshold: {TEST_LEVENSHTEIN_THRESHOLD}
      rule7_ignore_words: ["browns"]
"""


@pytest.mark.asyncio()
async def test_normal_case(mock_reddit: Mock) -> None:
    """Test the normal case for get_config."""
    sr = await mock_reddit.subreddit()
    wiki_page = await sr.wiki.get_page()
    wiki_page.content_md = TEST_CONFIG
    config = await get_config(mock_reddit, "subreddit_name")

    assert config
    assert isinstance(config, Config)
    assert config.enable_automatic_downvotes is False
    assert config.enable_automatic_sidebar_scores is False
    assert config.downvotes_delay == timedelta(days=-1).total_seconds()
    assert config.rule7_levenshtein_threshold == TEST_LEVENSHTEIN_THRESHOLD


@pytest.mark.asyncio()
async def test_blank_page_returns_defaults(mock_reddit: Mock) -> None:
    """Test the normal case for get_config."""
    sr = await mock_reddit.subreddit()
    wiki_page = await sr.wiki.get_page()
    wiki_page.content_md = ""

    config = await get_config(mock_reddit, "subreddit_name")

    assert config
    assert isinstance(config, Config)
    assert config.enable_automatic_downvotes is False
    assert config.enable_automatic_sidebar_scores is False
    assert config.downvotes_delay == timedelta(days=-1).total_seconds()
    assert config.rule7_levenshtein_threshold == TEST_LEVENSHTEIN_THRESHOLD
