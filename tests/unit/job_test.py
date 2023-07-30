from collections.abc import Awaitable, Callable
from unittest.mock import ANY, AsyncMock, Mock, patch

import pytest

from otto.config import Config


async def _fake_repeat(_: int, func: Callable[..., Awaitable[None]]) -> None:
    await func()


@pytest.mark.asyncio()
async def test_main(
    mock_get_reddit: AsyncMock,
    mock_reddit: Mock,
    mock_get_config: AsyncMock,
    mock_config: Mock,
) -> None:
    """Test the main function."""
    sr_name = "test_sr_name"
    with (
        patch("otto.job.get_reddit", mock_get_reddit),
        patch("otto.job.get_config", mock_get_config),
        patch("otto.job.repeat", wraps=_fake_repeat) as mock_repeat,
        patch("otto.job.run_jobs", autospec=True) as mock_run_jobs,
    ):
        from otto.job import REPEAT_SECONDS, main

        await main(sr_name)

    mock_get_config.assert_called_once_with(mock_reddit, sr_name)
    mock_repeat.assert_called_once_with(REPEAT_SECONDS, ANY)
    mock_run_jobs.assert_called_once_with(mock_config, mock_reddit, sr_name)


@pytest.mark.asyncio()
async def test_run_jobs(mock_nfl_client: Mock, mock_reddit: Mock) -> None:
    """Test that run_jobs calls the expected functions with the expected arguments."""
    config = Mock(spec=Config, enable_automatic_sidebar_scores=True, enable_automatic_downvotes=True)
    games = mock_nfl_client().get_scores.return_value
    records = mock_nfl_client().get_standings.return_value

    with (
        patch("otto.job.NFLClient", mock_nfl_client),
        patch("otto.job.update_sidebar_score") as mock_update_sidebar_score,
        patch("otto.job.update_downvote") as mock_update_downvote,
    ):
        from otto.job import run_jobs

        await run_jobs(config, mock_reddit, "test_sr_name")

    mock_update_sidebar_score.assert_called_once_with(mock_reddit, "test_sr_name", games, records)
    mock_update_downvote.assert_called_once_with(config, mock_reddit, "test_sr_name", games)


@pytest.mark.asyncio()
async def test_run_jobs_errors(mock_nfl_client: Mock, mock_reddit: Mock) -> None:
    """Test that run_jobs calls the expected functions with the expected arguments."""
    config = Mock(spec=Config, enable_automatic_sidebar_scores=True, enable_automatic_downvotes=True)
    games = mock_nfl_client().get_scores.return_value
    records = mock_nfl_client().get_standings.return_value

    with (
        patch("otto.job.NFLClient", mock_nfl_client),
        patch("otto.job.update_sidebar_score", side_effect=ValueError) as mock_update_sidebar_score,
        patch("otto.job.update_downvote", side_effect=ValueError) as mock_update_downvote,
        patch("otto.job.logger") as mock_logger,
    ):
        from otto.job import run_jobs

        await run_jobs(config, mock_reddit, "test_sr_name")

    exception_count = 2
    assert mock_logger.exception.call_count == exception_count
    mock_update_sidebar_score.assert_called_once_with(mock_reddit, "test_sr_name", games, records)
    mock_update_downvote.assert_called_once_with(config, mock_reddit, "test_sr_name", games)
