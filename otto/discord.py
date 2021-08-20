import logging
import sys

from random import choice

import discord

from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_commands import remove_all_commands
from discord_slash.utils.manage_commands import remove_all_commands_in

from otto import DISCORD_BOT_ID
from otto import DISCORD_GUILD_ID
from otto import DISCORD_TOKEN
from otto import get_reddit
from otto import SUBREDDIT_NAME
from otto.lib.game_thread import generate_game_thread
from otto.lib.mod_actions import disable_text_posts
from otto.lib.mod_actions import enable_text_posts
from otto.lib.update_sidebar_image import update_sidebar_image
from otto.types import SendMessage


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("otto.discord")

bot = commands.Bot(command_prefix="/", intents=discord.Intents.default())
commands = SlashCommand(bot, sync_commands=True)

reddit = get_reddit()
guild_ids = [int(DISCORD_GUILD_ID or 0)]


def generate_send_message(ctx: SlashContext) -> SendMessage:
    async def send(message: str) -> None:
        await ctx.send(content=message)

    return send


@bot.event
async def on_ready() -> None:
    logger.info("Removing all commands")
    # await remove_all_commands(DISCORD_BOT_ID, DISCORD_TOKEN)
    # await remove_all_commands_in(DISCORD_BOT_ID, DISCORD_TOKEN, DISCORD_GUILD_ID)
    pass


@commands.slash(
    name="sidebar",
    description="Update sidebar image in old and new reddit",
    guild_ids=guild_ids,
    options=[
        create_option(
            name="url",
            description="url of image to set as the sidebar",
            option_type=SlashCommandOptionType.STRING,
            required=True,
        )
    ],
)
async def sidebar(ctx: SlashContext, url: str) -> None:
    try:
        await update_sidebar_image(
            reddit=get_reddit(), image_url=url, send_message=generate_send_message(ctx)
        )
    except BaseException as err:
        await ctx.send(f"```{err}```")
        logger.error("/sidebar failed", exc_info=True)


@commands.slash(
    name="compliment",
    description="Feeling down? This might be the pick-me-up you need!",
    guild_ids=guild_ids,
    options=[
        create_option(
            name="name",
            description="Optional name of user to compliment",
            option_type=SlashCommandOptionType.USER,
            required=False,
        )
    ],
)
async def compliment(ctx: SlashContext, name: str) -> None:
    username = name if name else getattr(ctx.author, "name", "")
    messages = [
        f"You look nice today, {username}",
        f"{username}, you're awesome!",
        f"{username}, you're the Jarvis to my OBJ",
    ]
    await ctx.send(choice(messages))


@commands.slash(
    name="enable_text_posts",
    description="Enable text posts, allowing self posts and link posts",
    guild_ids=guild_ids,
)
async def enable_text_posts_handler(ctx: SlashContext) -> None:
    await enable_text_posts(get_reddit(), SUBREDDIT_NAME, generate_send_message(ctx))


@commands.slash(
    name="disable_text_posts",
    description="Disable text posts, by only allowing link posts",
    guild_ids=guild_ids,
)
async def disable_text_posts_handler(ctx: SlashContext) -> None:
    """Disable text posts by only allowing link posts"""
    await disable_text_posts(get_reddit(), SUBREDDIT_NAME, generate_send_message(ctx))


@commands.slash(
    name="generate_game_thread",
    description="Generate game day threads",
    guild_ids=guild_ids,
)
async def game_day_thread(ctx: SlashContext) -> None:
    await generate_game_thread(generate_send_message(ctx))


if __name__ == "__main__":
    logger.info("Starting otto as discord bot")
    bot.run(DISCORD_TOKEN)
