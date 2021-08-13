import asyncio
import logging
import sys

from random import random
from typing import Callable

import discord

from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash import SlashContext
from discord_slash.model import SlashCommandOptionType
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_commands import remove_all_commands

from otto import DISCORD_BOT_ID
from otto import DISCORD_TOKEN
from otto import get_reddit
from otto import SUBREDDIT_NAME
from otto.lib.game_thread import generate_game_thread
from otto.lib.mod_actions import disable_text_posts
from otto.lib.mod_actions import enable_text_posts
from otto.lib.update_sidebar_image import update_sidebar_image


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("otto.discord")

bot = commands.Bot(command_prefix="/", intents=discord.Intents.default())
commands = SlashCommand(bot, sync_commands=True)

reddit = get_reddit()


def slash_send(ctx: SlashContext) -> Callable[[str], None]:
    def send(message: str) -> None:
        asyncio.run(ctx.send(content=message))

    return send


@commands.slash(
    name="sidebar",
    description="Update sidebar image in old and new reddit",
    options=[
        create_option(
            name="url",
            description="url of image to set as the sidebar",
            option_type=SlashCommandOptionType.STRING,
            required=True,
        )
    ],
)
def sidebar(ctx: SlashContext, url: str) -> None:
    update_sidebar_image(
        reddit=get_reddit(), image_url=url, send_message=slash_send(ctx)
    )


@commands.slash(
    name="compliment",
    description="Feeling down? This might be the pick-me-up you need!",
    options=[
        create_option(
            name="name",
            description="Optional name of user to compliment",
            option_type=SlashCommandOptionType.USER,
            required=False,
        )
    ],
)
def compliment(ctx: SlashContext, username: str = None) -> None:
    """
    Feeling down? This might be the pick-me-up you need! :D

    Username is optional, will assume current user if not specified
    """
    username = username if username else getattr(ctx.author, "name", "")
    messages = [
        f"You look nice today, {username}",
        f"{username}, you're awesome!",
        f"{username}, you're the Jarvis to my OBJ",
    ]
    slash_send(ctx)(random.choice(messages))


@commands.slash(
    name="enable_text_posts",
    description="Enable text posts, allowing self posts and link posts",
)
def enable_text_posts_handler(ctx: SlashContext) -> None:
    enable_text_posts(get_reddit(), SUBREDDIT_NAME, slash_send(ctx))


@commands.slash(
    name="disable_text_posts",
    description="Disable text posts, by only allowing link posts",
)
def disable_text_posts_handler(ctx: SlashContext) -> None:
    """Disable text posts by only allowing link posts"""
    disable_text_posts(get_reddit(), SUBREDDIT_NAME, slash_send(ctx))


@commands.slash(name="generate_game_thread", description="Generate game day threads")
def game_day_thread(ctx: SlashContext) -> None:
    generate_game_thread(get_reddit(), SUBREDDIT_NAME, slash_send(ctx))


if __name__ == "__main__":
    logger.info("Removing all commands")
    asyncio.run(remove_all_commands(DISCORD_BOT_ID, DISCORD_TOKEN))

    logger.info("Starting the bot")
    bot.run(DISCORD_TOKEN)
