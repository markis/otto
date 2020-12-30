import logging

from typing import Callable

import praw
import tinycss2

from otto import SUBREDDIT_NAME
from otto.errors import SidebarBackgroundImageError
from otto.utils import delete_file
from otto.utils import download_image
from otto.utils.image import get_image_size
from otto.utils.image import resize_image


logger = logging.getLogger(__name__)


def update_sidebar_image(
    reddit: praw.Reddit,
    image_url: str,
    send_message: Callable[[str], None],
    sr_name: str = SUBREDDIT_NAME,
) -> None:
    send_message("Downloading Image")
    image_path = download_image(image_url)
    sr_browns = reddit.subreddit(sr_name)

    send_message("Resizing Image")
    resize_image_path = resize_image(image_path)
    send_message("Updating new reddit")
    update_new_reddit_sidebar_image(sr_browns, resize_image_path)
    send_message("Updating old reddit")
    update_old_reddit_sidebar_image(sr_browns, resize_image_path)

    send_message("Cleaning up temporary files")
    delete_file(image_path)
    delete_file(resize_image_path)

    send_message("Sidebar updated")


def update_new_reddit_sidebar_image(sr: praw.models.Subreddit, image_path: str) -> None:
    widgets = sr.widgets
    image_url = widgets.mod.upload_image(image_path)
    width, height = get_image_size(image_path)
    image_dicts = [{"width": width, "height": height, "linkUrl": "", "url": image_url}]

    for widget in widgets.sidebar:
        if isinstance(widget, praw.models.ImageWidget):
            widget.mod.update(data=image_dicts)
            break


def update_old_reddit_sidebar_image(sr: praw.models.Subreddit, image_path: str) -> None:
    # Update old Reddit
    SIDEBAR_TOKEN = "sidebar"
    SIDEBAR_CSS_NAME = "h1.redditname"

    width, height = get_image_size(image_path)
    sr_stylesheet = sr.stylesheet
    styles = sr_stylesheet.__call__()
    css = styles.stylesheet

    try:
        sr_stylesheet.upload(SIDEBAR_TOKEN, image_path)
    except praw.exceptions.APIException:
        raise
    except praw.exceptions.PRAWException:
        raise

    parsed = tinycss2.parse_stylesheet(css)
    for rule in parsed:
        if isinstance(rule, tinycss2.ast.QualifiedRule):
            identity = "".join(
                [token.value for token in rule.prelude if hasattr(token, "value")]
            ).strip()
            if identity == SIDEBAR_CSS_NAME:
                url_token = None
                height_token = None
                width_token = None
                set_next_url_token = False
                for token in rule.content:
                    if token.value == "background-image":
                        set_next_url_token = True
                    elif set_next_url_token and isinstance(
                        token, tinycss2.ast.URLToken
                    ):
                        url_token = token
                        set_next_url_token = False
                        break

                for token in rule.content:
                    if token.value == "width":
                        set_next_url_token = True
                    elif set_next_url_token and isinstance(
                        token, tinycss2.ast.DimensionToken
                    ):
                        width_token = token
                        set_next_url_token = False
                        break

                for token in rule.content:
                    if token.value == "height":
                        set_next_url_token = True
                    elif set_next_url_token and isinstance(
                        token, tinycss2.ast.DimensionToken
                    ):
                        height_token = token
                        set_next_url_token = False
                        break

                if url_token:
                    sidebar_token = "%%" + SIDEBAR_TOKEN + "%%"
                    if url_token.value != sidebar_token:
                        url_token.value = sidebar_token
                else:
                    raise SidebarBackgroundImageError()

                if height_token and width_token:
                    if width > height and width < 600:
                        height_token.representation = str(height)
                        width_token.representation = "300"
                    elif width > height and width >= 600:
                        height_token.representation = str(int(height / 2))
                        width_token.representation = "300"
                    else:
                        width_token.representation = "300"
                        height_token.representation = "400"

    updated_css = "".join([rule.serialize() for rule in parsed])
    sr_stylesheet.update(updated_css)
