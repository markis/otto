import logging
from typing import Final

import tinycss2.ast
import tinycss2.parser
from asyncpraw import Reddit
from asyncpraw.models.reddit.subreddit import Subreddit
from asyncpraw.models.reddit.widgets import ImageWidget, SubredditWidgets
from discord import ApplicationContext
from discord.file import File

from otto.utils import delete_file, download_image
from otto.utils.image import resize_image

SIDEBAR_TOKEN: Final = "sidebar"
SIDEBAR_CSS_NAME: Final = "h1.redditname"

logger: Final = logging.getLogger(__name__)


async def update_sidebar_image(reddit: Reddit, image_url: str, sr_name: str, ctx: ApplicationContext) -> None:
    image_path = download_image(image_url)
    sr_browns = await reddit.subreddit(sr_name)

    resize_image_path, width, height = resize_image(image_path)
    await update_new_reddit_sidebar_image(sr_browns, resize_image_path, width, height)
    await update_old_reddit_sidebar_image(sr_browns, resize_image_path, width, height)

    await delete_file(image_path)

    # add the image to final update
    picture = None
    with open(resize_image_path, "rb") as f:
        picture = File(f)
        await ctx.respond(content="Sidebar Updated", file=picture)

    # delete the image
    await delete_file(resize_image_path)


async def update_new_reddit_sidebar_image(sr: Subreddit, image_path: str, width: int, height: int) -> None:
    widgets: SubredditWidgets = await sr.widgets
    image_url = widgets.mod.upload_image(image_path)
    image_dicts = [{"width": width, "height": height, "linkUrl": "", "url": image_url}]

    for widget in await widgets.sidebar():
        if isinstance(widget, ImageWidget):
            widget.mod.update(data=image_dicts)
            break


def _update_background_image_token(rule: tinycss2.ast.QualifiedRule, sidebar_token: str) -> None:
    token_location = 0
    # find the location of background-image token
    for i, token in enumerate(rule.content):
        if isinstance(token, tinycss2.ast.IdentToken) and token.lower_value == "background-image":
            token_location = i
            break

    # update the the value
    for token in rule.content[token_location:]:
        if isinstance(token, tinycss2.ast.URLToken):
            token.value = sidebar_token
            return
        elif isinstance(token, tinycss2.ast.FunctionBlock):
            argument: tinycss2.ast.StringToken = token.arguments[0]
            argument.value = f'"{sidebar_token}"'
            return
    return


def _update_size_token(rule: tinycss2.ast.QualifiedRule, identity: str, representation: str) -> None:
    token_location = 0
    # find the location of identity token by name
    for i, token in enumerate(rule.content):
        if isinstance(token, tinycss2.ast.IdentToken) and token.value == identity:
            token_location = i
            break
    # update the the value
    for token in rule.content[token_location:]:
        if isinstance(token, tinycss2.ast.DimensionToken):
            token.representation = representation
            return


async def update_old_reddit_sidebar_image(sr: Subreddit, image_path: str, width: int, height: int) -> None:
    # Update old Reddit

    sr_stylesheet = sr.stylesheet
    styles = sr_stylesheet.__call__()
    css = styles.stylesheet

    sr_stylesheet.upload(SIDEBAR_TOKEN, image_path)

    parsed = tinycss2.parser.parse_stylesheet(css)
    for rule in parsed:
        if isinstance(rule, tinycss2.ast.QualifiedRule):
            identity = "".join([token.value for token in rule.prelude if hasattr(token, "value")]).strip()
            if identity == SIDEBAR_CSS_NAME:
                width_token_representation = "300"
                height_token_representation = "400"
                if width > height and width < 600:
                    height_token_representation = str(height)
                    width_token_representation = "300"
                elif width > height and width >= 600:
                    height_token_representation = str(int(height / 2))
                    width_token_representation = "300"

                _update_background_image_token(rule, f"%%{SIDEBAR_TOKEN}%%")
                _update_size_token(rule, "height", height_token_representation)
                _update_size_token(rule, "width", width_token_representation)

    updated_css = "".join([rule.serialize() for rule in parsed])
    sr_stylesheet.update(updated_css)
