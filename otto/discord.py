import logging
import sys
import tempfile
from random import choice
from typing import Final

import discord
from discord.user import User

from otto import get_reddit
from otto.constants import DISCORD_GUILD_ID, DISCORD_TOKEN, SUBREDDIT_NAME
from otto.lib.game_thread import generate_game_thread
from otto.lib.mod_actions import disable_text_posts, enable_text_posts
from otto.lib.screenshot import screenshot_article
from otto.lib.update_sidebar_image import update_sidebar_image
from otto.types import SendMessage
from otto.utils.timer import Timer

logger: Final = logging.getLogger("otto.discord")
logging.basicConfig(stream=sys.stdout, level=logging.WARN)

guild_ids: Final = [int(DISCORD_GUILD_ID or 0)]
bot: Final = discord.Bot(
    "Otto Grahaminator",
    debug_guilds=guild_ids,
    intents=discord.Intents(messages=True, message_content=True),
)


def run() -> None:
    """Run the discord bot."""
    logger.info("Starting otto as discord bot!")
    bot.run(DISCORD_TOKEN)


def generate_send_message(ctx: discord.ApplicationContext) -> SendMessage:
    """Generate a send message function for the given context."""

    async def send(message: str) -> None:
        await ctx.respond(content=message)

    return send


@bot.event
async def on_message(_: discord.Message) -> None:
    """Handle a message event."""
    logger.info("on_message")


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
    try:
        with Timer() as t:
            await ctx.defer()
            with tempfile.NamedTemporaryFile(suffix=".png") as temp_file:
                if await screenshot_article(url, temp_file.name):
                    screenshot = discord.File(temp_file.name)
                    await ctx.respond("Screenshot", file=screenshot)
        logger.info("Screenshot took %.4f", t.elapsed)
    except BaseException as err:
        await ctx.respond(f'/screenshot "{url}" failed \n ```{err}```')
        logger.exception('/screenshot "%s" failed', url)


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
    try:
        await ctx.defer()
        async with get_reddit() as reddit:
            await update_sidebar_image(reddit=reddit, sr_name=SUBREDDIT_NAME, image_url=url, ctx=ctx)
    except BaseException as err:
        await ctx.respond(f'/sidebar "{url}" failed \n ```{err}```')
        logger.exception('/sidebar "%s" failed', url)


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
    try:
        username = name if type(name) is str else name.mention if type(name) is User else ctx.author.mention
        messages = [
            f"You look nice today, {username}",
            f"{username}, you're awesome!",
        ]
        await ctx.respond(choice(messages))  # noqa: S311
    except BaseException as err:
        await ctx.respond(f'/compliment "{name}" failed \n ```{err}```')
        logger.exception('/compliment "%s" failed', name)


@bot.slash_command(name="enable_text_posts", description="Enable text posts, allowing self posts and link posts")
async def enable_text_posts_handler(ctx: discord.ApplicationContext) -> None:
    """Enable text posts, allowing self posts and link posts."""
    try:
        await ctx.defer()
        async with get_reddit() as reddit:
            await enable_text_posts(reddit, SUBREDDIT_NAME, generate_send_message(ctx))
    except BaseException as err:
        await ctx.respond(f"/enable_text_posts failed \n ```{err}```")
        logger.exception("/enable_text_posts failed")


@bot.slash_command(name="disable_text_posts", description="Disable text posts, by only allowing link posts")
async def disable_text_posts_handler(ctx: discord.ApplicationContext) -> None:
    """Disable text posts, by only allowing link posts."""
    try:
        await ctx.defer()
        async with get_reddit() as reddit:
            await disable_text_posts(reddit, SUBREDDIT_NAME, generate_send_message(ctx))
    except BaseException as err:
        await ctx.respond(f"/disable_text_posts failed \n ```{err}```")
        logger.exception("/disable_text_posts failed")


@bot.slash_command(name="generate_game_thread", description="Generate game day threads")
async def game_day_thread(ctx: discord.ApplicationContext) -> None:
    """Generate game day thread."""
    try:
        await ctx.defer()
        await generate_game_thread(generate_send_message(ctx))
    except BaseException as err:
        await ctx.respond(f"/generate_game_thread failed \n ```{err}```")
        logger.exception("/generate_game_thread failed")


@bot.slash_command(name="ping", description="Sends the bot's latency.")
async def ping(ctx: discord.ApplicationContext) -> None:
    """Respond with the bot's latency."""
    await ctx.respond(f"Pong! Latency is {bot.latency}")


if __name__ == "__main__":
    run()
