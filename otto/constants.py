import inspect
import os
from datetime import UTC
from pathlib import Path
from typing import Final


def get_file_path() -> Path:
    """Get the path to the module directory."""
    try:
        return Path(__file__).parent
    except KeyError:  # pragma: no cover
        stack = inspect.stack()
        file = stack[1].filename
        return Path(file).parent


TEAM_NAME: Final = os.environ.get("TEAM_NAME", "CLE")
SUBREDDIT_NAME: Final = os.environ.get("SUBREDDIT_NAME", "Browns")
REDDIT_CLIENT_ID: Final = os.environ.get("REDDIT_CLIENT_ID")
REDDIT_CLIENT_SECRET: Final = os.environ.get("REDDIT_CLIENT_SECRET")
REDDIT_USERNAME: Final = os.environ.get("REDDIT_USERNAME")
REDDIT_PASSWORD: Final = os.environ.get("REDDIT_PASSWORD")
DISCORD_BOT_ID: Final = os.environ.get("DISCORD_BOT_ID")
DISCORD_GUILD_ID: Final = os.environ.get("DISCORD_GUILD_ID")
DISCORD_TOKEN: Final = os.environ.get("DISCORD_TOKEN")
TWITTER_AUTH_COOKIE: Final = os.environ.get("TWITTER_AUTH_COOKIE")
TWITTER_KEY: Final = os.environ.get("TWITTER_KEY")
TWITTER_SECRET: Final = os.environ.get("TWITTER_SECRET")
TWITTER_TOKEN: Final = os.environ.get("TWITTER_TOKEN")
TWITTER_TOKEN_SECRET: Final = os.environ.get("TWITTER_TOKEN_SECRET")
MODULE_DIRECTORY: Final = get_file_path()
ASSETS_DIRECTORY: Final = MODULE_DIRECTORY.parent / "assets"
DEFAULT_IMAGE_HEIGHT: Final = 400
DEFAULT_IMAGE_WIDTH: Final = 300
DEFAULT_TIMEOUT: Final = 10
TIMEZONE: Final = UTC
TRUTHY_VALUES: Final = ("1", "true", "yes")
