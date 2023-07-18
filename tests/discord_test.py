import logging
from operator import itemgetter
from typing import NoReturn
from unittest.mock import ANY, AsyncMock, Mock, patch

import discord
import pytest
from discord import File
from discord.bot import Bot
from discord.commands.context import ApplicationContext

from otto.constants import DISCORD_TOKEN, SUBREDDIT_NAME
from otto.discord import (
    compliment,
    disable_text_posts_handler,
    enable_text_posts_handler,
    error_handler,
    game_day_thread,
    on_message,
    ping,
    run,
    screenshot,
    sidebar,
)


@pytest.fixture()
def mock_discord_context() -> Mock:
    """Return a mock discord context."""
    return Mock(spec=ApplicationContext, defer=AsyncMock(), respond=AsyncMock())


def test_run() -> None:
    """Test the run function."""
    mock_logger = Mock(spec=logging.Logger)
    mock_bot = Mock(spec=Bot)

    with patch("otto.discord.logger", mock_logger), patch("otto.discord.bot", mock_bot):
        run()

    mock_logger.info.assert_called_once_with("Starting otto as discord bot!")
    mock_bot.run.assert_called_once_with(DISCORD_TOKEN)


@pytest.mark.asyncio()
async def test_on_message() -> None:
    """Test the on_message listener."""
    mock_logger = Mock(spec=logging.Logger)

    with patch("otto.discord.logger", mock_logger):
        await on_message(Mock(spec=discord.Message))

    mock_logger.info.assert_called_once_with("on_message")


@pytest.mark.asyncio()
async def test_error_handler_exception(mock_discord_context: Mock) -> None:
    """Test the error handler when an exception is raised."""

    async def test_function(ctx: discord.ApplicationContext) -> NoReturn:
        del ctx
        err_msg = "Test exception"
        raise ValueError(err_msg)

    decorated_function = error_handler(test_function)
    await decorated_function(mock_discord_context)
    mock_discord_context.respond.assert_called_once_with("/test_function  failed \n ```Test exception```")


@pytest.mark.asyncio()
async def test_screenshot_command(mock_discord_context: Mock) -> None:
    """Test the screenshot command."""
    screenshot_article_mock = AsyncMock(return_value=True)

    file_mock = Mock(spec=File)
    file_constructor_mock = Mock(return_value=file_mock)
    with (
        patch("tempfile.NamedTemporaryFile"),
        patch("otto.discord.screenshot_article", screenshot_article_mock),
        patch("otto.discord.discord.File", file_constructor_mock),
    ):
        url = "https://example.com"
        await screenshot(mock_discord_context, url)

    screenshot_article_mock.assert_awaited_once_with(url, ANY)
    file_constructor_mock.assert_called_once_with(ANY)
    mock_discord_context.respond.assert_called_once_with(ANY, file=file_mock)
    mock_discord_context.respond.assert_called_once_with(ANY, file=file_mock)


@pytest.mark.asyncio()
async def test_sidebar_command(mock_discord_context: Mock, mock_get_reddit: AsyncMock) -> None:
    """Test the sidebar command."""
    mock_update_sidebar_image = AsyncMock(return_value=None)

    with (
        patch("otto.discord.get_reddit", mock_get_reddit),
        patch("otto.discord.update_sidebar_image", mock_update_sidebar_image),
    ):
        url = "https://example.com/image.png"
        await sidebar(mock_discord_context, url)

    # Perform assertions
    mock_discord_context.defer.assert_called_once()
    mock_update_sidebar_image.assert_awaited_once_with(
        reddit=ANY,
        sr_name=SUBREDDIT_NAME,
        image_url=url,
        ctx=mock_discord_context,
    )


@pytest.mark.asyncio()
async def test_sidebar_command_error(mock_discord_context: Mock, mock_get_reddit: AsyncMock) -> None:
    """Test the sidebar command."""
    mock_update_sidebar_image = AsyncMock(return_value=None)

    with (
        patch("otto.discord.get_reddit", mock_get_reddit),
        patch("otto.discord.update_sidebar_image", mock_update_sidebar_image),
    ):
        url = "https://example.com/image.png"
        await sidebar(mock_discord_context, url)

    # Perform assertions
    mock_discord_context.defer.assert_called_once()
    mock_update_sidebar_image.assert_awaited_once_with(
        reddit=ANY,
        sr_name=SUBREDDIT_NAME,
        image_url=url,
        ctx=mock_discord_context,
    )


@pytest.mark.asyncio()
async def test_compliment_command_name_arg(mock_discord_context: Mock) -> None:
    """Test the compliment command."""
    name = "John Doe"

    with patch("otto.discord.choice", itemgetter(0)):
        await compliment(mock_discord_context, name)

    mock_discord_context.respond.assert_called_once_with(f"You look nice today, {name}")


@pytest.mark.asyncio()
async def test_compliment_command_context(mock_discord_context: Mock) -> None:
    """Test the compliment command."""
    mock_discord_context.author.mention = author = "@author"

    with patch("otto.discord.choice", itemgetter(0)):
        await compliment(mock_discord_context)

    mock_discord_context.respond.assert_called_once_with(f"You look nice today, {author}")


@pytest.mark.asyncio()
async def test_disable_text_posts_handler(mock_discord_context: Mock, mock_get_reddit: AsyncMock) -> None:
    """Test the enable text posts handler."""
    mock_disable_text_posts = AsyncMock(return_value="Text posts disabled")

    with (
        patch("otto.discord.get_reddit", mock_get_reddit),
        patch("otto.discord.disable_text_posts", mock_disable_text_posts),
    ):
        await disable_text_posts_handler(mock_discord_context)

    mock_discord_context.defer.assert_called_once()
    mock_disable_text_posts.assert_awaited_once_with(ANY, ANY)
    mock_discord_context.respond.assert_called_once_with("Text posts disabled")


@pytest.mark.asyncio()
async def test_enable_text_posts_handler(mock_discord_context: Mock, mock_get_reddit: AsyncMock) -> None:
    """Test the enable text posts handler."""
    mock_enable_text_posts = AsyncMock(return_value="Text posts enabled")

    with (
        patch("otto.discord.get_reddit", mock_get_reddit),
        patch("otto.discord.enable_text_posts", mock_enable_text_posts),
    ):
        await enable_text_posts_handler(mock_discord_context)

    mock_discord_context.defer.assert_called_once()
    mock_enable_text_posts.assert_awaited_once_with(ANY, ANY)
    mock_discord_context.respond.assert_called_once_with("Text posts enabled")


@pytest.mark.asyncio()
async def test_game_day_thread_command(mock_discord_context: Mock) -> None:
    """Test the game day thread command."""
    generate_game_thread_mock = AsyncMock(return_value="Generated game thread")

    with patch("otto.discord.generate_game_thread", generate_game_thread_mock):
        await game_day_thread(mock_discord_context)

    mock_discord_context.defer.assert_called_once()
    mock_discord_context.respond.assert_called_once_with("Generated game thread")


@pytest.mark.asyncio()
async def test_ping_command(mock_discord_context: Mock) -> None:
    """Test the ping command."""
    mock_bot = Mock(spec=Bot, latency=0.123)

    with patch("otto.discord.bot", mock_bot):
        await ping(mock_discord_context)

    mock_discord_context.respond.assert_called_once_with("Pong! Latency is 0.123")
