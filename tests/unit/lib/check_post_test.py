from unittest.mock import AsyncMock, Mock, patch

import pytest
from asyncpraw.models import Submission
from asyncpraw.models.reddit.submission import SubmissionModeration

from otto.config import Config
from otto.lib.check_posts import check_post


@pytest.fixture()
def mock_submission() -> Mock:
    """Mock a submission."""
    submission_mod = Mock(spec=SubmissionModeration)
    return AsyncMock(
        spec=Submission,
        id=1,
        title="browns related",
        url="https://twitter.com/browns/status/1234567890",
        approved_by=None,
        mod=submission_mod,
    )


@pytest.mark.asyncio()
@pytest.mark.parametrize(
    ("threshold", "tweet_text", "submission_text", "expected"),
    [
        (100, "Tweet about something browns related", "browns related", True),
        (100, "Tweet about something else", "not browns related", False),
        (75, "Tweet about something browns related", "browns related", True),
        (75, "Tweet about something else", "not browns related", False),
        (0, "Tweet about somethinz browns related", "browns related", True),
        (0, "Tweet about somethinz else", "not browns related", True),
    ],
)
async def test_check_post(
    mock_submission: Mock,
    *,
    threshold: int,
    tweet_text: str,
    submission_text: str,
    expected: bool,
) -> None:
    """Test the normal case for check_post."""
    config = Mock(spec=Config, rule7_levenshtein_threshold=threshold)
    mock_submission.title = submission_text

    with patch("otto.lib.check_posts.get_tweet_text") as get_tweet_text, patch("otto.lib.check_posts.logger"):
        get_tweet_text.return_value = tweet_text
        await check_post(config, mock_submission)

    if expected:
        assert mock_submission.approved_by is None
        assert get_tweet_text.called
        assert mock_submission.reply.called
        assert not mock_submission.mod.flair.called
        assert not mock_submission.report.called
    else:
        assert mock_submission.approved_by is None
        assert get_tweet_text.called
        assert mock_submission.reply.called
        assert mock_submission.mod.flair.called
        assert mock_submission.report.called


@pytest.mark.asyncio()
async def test_check_post_do_nothing_when_approved(mock_submission: Mock) -> None:
    """Test that check_post does nothing when the post is already approved."""
    config = Mock(spec=Config, rule7_levenshtein_threshold=75)
    mock_submission.approved_by = "someone"

    with patch("otto.lib.check_posts.get_tweet_text") as get_tweet_text, patch("otto.lib.check_posts.logger") as logger:
        await check_post(config, mock_submission)

    assert mock_submission.approved_by == "someone"
    assert logger.info.called
    assert not get_tweet_text.called
    assert not mock_submission.reply.called
    assert not mock_submission.mod.flair.called
    assert not mock_submission.report.called
