import logging
import sys
import tempfile
from collections.abc import Awaitable, Callable
from functools import wraps
from random import choice
from typing import Final, ParamSpec, cast

import discord
from discord.user import User

from otto import get_reddit
from otto.constants import DISCORD_GUILD_ID, DISCORD_TOKEN, SUBREDDIT_NAME
from otto.lib.game_thread import generate_game_thread
from otto.lib.mod_actions import disable_text_posts, enable_text_posts
from otto.lib.screenshot import screenshot_article
from otto.lib.update_sidebar_image import update_sidebar_image
from otto.utils.timer import Timer

logger: Final = logging.getLogger("otto.discord")
logging.basicConfig(stream=sys.stdout, level=logging.WARN)

guild_ids: Final = [int(DISCORD_GUILD_ID or 0)]
bot: Final = discord.Bot(
    "Otto Grahaminator",
    debug_guilds=guild_ids,
    intents=discord.Intents(messages=True, message_content=True),
)

P = ParamSpec("P")


def run() -> None:
    """Run the discord bot."""
    logger.info("Starting otto as discord bot!")
    bot.run(DISCORD_TOKEN)


def error_handler(func: Callable[P, Awaitable[None]]) -> Callable[P, Awaitable[None]]:
    """Handle errors for slash commands."""

    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> None:
        try:
            await func(*args, **kwargs)
        except Exception as err:
            ctx = cast(discord.ApplicationContext, args[0])
            arguments = " ".join(map(str, args[1:]))
            await ctx.respond(f"/{func.__name__} {arguments} failed \n ```{err}```")
            logger.exception("/%s %s failed", func.__name__, arguments)

    return wrapper


@bot.event
async def on_message(_: discord.Message) -> None:
    """Handle a message event."""
    logger.info("on_message")


@error_handler
@bot.slash_command(
    name="screenshot",
    description="Take a screenshot of a webpage",
    options=[
        discord.Option(
            name="url",
            description="url of webpage to screenshot",
            option_type=str,
            required=True,
        ),
    ],
)
async def screenshot(ctx: discord.ApplicationContext, url: str) -> None:
    """Take a screenshot of a webpage."""
    with Timer() as t:
        await ctx.defer()
        with tempfile.NamedTemporaryFile(suffix=".png") as temp_file:
            if await screenshot_article(url, temp_file.name):
                screenshot = discord.File(temp_file.name)
                await ctx.respond(url, file=screenshot)
    logger.info("Screenshot took %.4f", t.elapsed)


@error_handler
@bot.slash_command(
    name="sidebar",
    description="Update sidebar image in old and new reddit",
    options=[
        discord.Option(
            name="url",
            description="url of image to set as the sidebar",
            option_type=str,
            required=True,
        ),
    ],
)
async def sidebar(ctx: discord.ApplicationContext, url: str) -> None:
    """Update sidebar image in old and new reddit."""
    await ctx.defer()
    async with get_reddit() as reddit:
        await update_sidebar_image(reddit=reddit, sr_name=SUBREDDIT_NAME, image_url=url, ctx=ctx)


@error_handler
@bot.slash_command(
    name="compliment",
    description="Feeling down? This might be the pick-me-up you need!",
    options=[
        discord.Option(
            name="name",
            description="Optional name of user to compliment",
            input_type=discord.User,
            required=False,
        ),
    ],
)
async def compliment(ctx: discord.ApplicationContext, name: User | str | None = None) -> None:
    """Compliment a user."""
    username = name if type(name) is str else name.mention if type(name) is User else ctx.author.mention
    messages = [
        f"You look nice today, {username}",
        f"{username}, you're awesome!",
    ]
    await ctx.respond(choice(messages))  # noqa: S311


@error_handler
@bot.slash_command(name="enable_text_posts", description="Enable text posts, allowing self posts and link posts")
async def enable_text_posts_handler(ctx: discord.ApplicationContext) -> None:
    """Enable text posts, allowing self posts and link posts."""
    await ctx.defer()
    async with get_reddit() as reddit:
        result = await enable_text_posts(reddit, SUBREDDIT_NAME)
    await ctx.respond(result)


@error_handler
@bot.slash_command(name="disable_text_posts", description="Disable text posts, by only allowing link posts")
async def disable_text_posts_handler(ctx: discord.ApplicationContext) -> None:
    """Disable text posts, by only allowing link posts."""
    await ctx.defer()
    async with get_reddit() as reddit:
        result = await disable_text_posts(reddit, SUBREDDIT_NAME)
    await ctx.respond(result)


@error_handler
@bot.slash_command(name="generate_game_thread", description="Generate game day threads")
async def game_day_thread(ctx: discord.ApplicationContext) -> None:
    """Generate game day thread."""
    await ctx.defer()
    game_thread_message = await generate_game_thread()
    await ctx.respond(game_thread_message)


@error_handler
@bot.slash_command(name="ping", description="Sends the bot's latency.")
async def ping(ctx: discord.ApplicationContext) -> None:
    """Respond with the bot's latency."""
    await ctx.respond(f"Pong! Latency is {bot.latency}")


if __name__ == "__main__":
    run()  # pragma: no cover
