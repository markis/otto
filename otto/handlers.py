import logging
import random

from shlex import split
from typing import Any
from typing import Callable
from typing import Optional

import click
import praw

from otto import get_reddit
from otto.lib.game_thread import generate_game_thread
from otto.lib.mod_actions import ban_user
from otto.lib.mod_actions import disable_text_posts
from otto.lib.mod_actions import enable_text_posts
from otto.lib.update_sidebar_image import update_sidebar_image


logger = logging.getLogger(__name__)


@click.group(options_metavar="", add_help_option=False)
def otto() -> None:
    """
    Otto Grahaminator - ultimate moderator of r/Browns
    """
    pass


class OttoHelpFormatter(click.HelpFormatter):
    command: Optional[str]
    skip_usage: bool
    text: str

    def __init__(self, skip_usage: bool = False, command: Optional[str] = None) -> None:
        self.text = ""
        self.command = command
        self.skip_usage = skip_usage
        super().__init__(width=9999)

    def write(self, text: str) -> None:
        self.text += text

    def write_usage(self, prog: str, args: str = "", prefix: str = "Usage: ") -> None:
        if not self.skip_usage:
            prog = self.command if self.command else prog
            super().write_usage(prog, args, prefix)


class OttoContext(object):
    reddit: praw.Reddit
    sr_name: str
    username: str
    _send_message: Any

    def __init__(
        self,
        reddit: praw.Reddit,
        sr_name: str,
        send_message: Callable[[str], None],
        username: str,
    ) -> None:
        self.reddit = reddit
        self.sr_name = sr_name
        self.username = username
        self._send_message = send_message

    def send_message(self, message: str) -> None:
        self._send_message(message)


@otto.command(name="/help", options_metavar="", add_help_option=False)
@click.option("--name", help="subcommand to get help information about", required=False)
@click.pass_context
def help(click_ctx: click.Context, name: Optional[str] = None) -> None:
    """
    Print help for each command (ex: /help sidebar)
    """
    ctx: OttoContext = click_ctx.obj

    if not name:
        formatter = OttoHelpFormatter(skip_usage=True)
        otto.format_help(click_ctx, formatter)
        ctx.send_message(formatter.text)
    elif name:
        name = "/" + name.strip("/")
        cmd = otto.get_command(click_ctx, name)
        if cmd:
            # click_ctx.send_message(cmd.get_help(sub_click_ctx))
            formatter = OttoHelpFormatter(command=name)
            cmd.format_help(click_ctx, formatter)
            ctx.send_message(formatter.text)


@otto.command(name="/sidebar", options_metavar="", add_help_option=False)
@click.option(
    "--url",
    metavar="[url]",
    help="url of image to set as the sidebar",
    type=str,
    required=True,
)
@click.pass_obj
def sidebar(ctx: OttoContext, url: str) -> None:
    """
    Update sidebar image in old and new reddit

    Will attempt to resize the image down to 600x800 while maintaining aspect ratio.
    If it's smaller then it will attempt to resize down to 300x400.
    """

    update_sidebar_image(
        reddit=ctx.reddit, image_url=url, send_message=ctx.send_message
    )


@otto.command(name="/compliment", options_metavar="", add_help_option=False)
@click.option(
    "--username",
    metavar="[username]",
    help="username to compliment",
    type=str,
    required=False,
)
@click.pass_obj
def compliment(ctx: OttoContext, username: str) -> None:
    """
    Feeling down? This might be the pick-me-up you need! :D

    Username is optional, will assume current user if not specified
    """
    username = username if username else ctx.username
    messages = [
        f"You look nice today, @{username}",
        f"@{username}, you're awesome!",
        f"@{username}, you're the Jarvis to my OBJ",
    ]
    ctx.send_message(random.choice(messages))


@otto.command(name="/ban", options_metavar="", add_help_option=False)
@click.option(
    "--username", metavar="[username]", help="username to ban", type=str, required=True
)
@click.option(
    "-r",
    "--rule",
    metavar="[1-14]",
    help="violated rule or ban reason, use the number of the rule the user violated",
    type=click.IntRange(1, 14, clamp=True),
    required=True,
)
@click.option(
    "-n",
    "--note",
    metavar="[note]",
    help="note about the ban, not sent to the user",
    type=str,
    required=False,
)
@click.option(
    "-d",
    "--duration",
    metavar="[days]",
    help="duration of the ban, in days [default: permanent]",
    type=int,
    required=False,
)
@click.option(
    "-m",
    "--message",
    metavar="[message]",
    help="message about the ban sent to the user",
    type=str,
    required=False,
)
@click.pass_obj
def ban(
    ctx: OttoContext,
    username: str,
    rule: int,
    note: Optional[str] = None,
    duration: Optional[int] = None,
    message: Optional[str] = None,
) -> None:
    """
    Ban a user from r/Browns

    example: /ban markistest -d 4 -r 1 -n "Stupid test account" -m "Markis, stop being a test account"

    """
    ban_user(
        reddit=ctx.reddit,
        sr_name=ctx.sr_name,
        send_message=ctx.send_message,
        mod_name=ctx.username,
        user_name=username,
        rule_violation=rule,
        duration=duration,
        ban_message=message,
        note=note,
    )


@otto.command(name="/enable_text_posts", options_metavar="", add_help_option=False)
@click.pass_obj
def enable_text_posts_handler(ctx: OttoContext) -> None:
    """Enable text posts, allowing self posts and link posts"""
    enable_text_posts(ctx.reddit, ctx.sr_name, ctx.send_message)


@otto.command(name="/disable_text_posts", options_metavar="", add_help_option=False)
@click.pass_obj
def disable_text_posts_handler(ctx: OttoContext) -> None:
    """Disable text posts by only allowing link posts"""
    disable_text_posts(ctx.reddit, ctx.sr_name, ctx.send_message)


@otto.command(name="/game_day_thread", options_metavar="", add_help_option=False)
@click.pass_obj
def game_day_thread(ctx: OttoContext) -> None:
    """Generate game day threads"""
    generate_game_thread(ctx.reddit, ctx.sr_name, ctx.send_message)


@otto.command(name="/gdt", options_metavar="", add_help_option=False)
@click.pass_obj
def gdt(ctx: OttoContext) -> None:
    """Short cut for '/game_day_thread' """
    generate_game_thread(ctx.reddit, ctx.sr_name, ctx.send_message)


def execute_command(
    cmd_str: str, sr_name: str, send_message: Callable[[str], None], username: str
) -> None:
    try:
        logger.info(f"handling {cmd_str}")
        shlex_args = split(cmd_str)
        ctx = otto.make_context("otto", shlex_args)
        args = otto.parse_args(ctx, shlex_args)
        obj = OttoContext(
            reddit=get_reddit(),
            send_message=send_message,
            username=username,
            sr_name=sr_name,
        )
        try:
            name, cmd, args = otto.resolve_command(ctx, args)
            ctx.invoked_subcommand = name
            sub_ctx = cmd.make_context(name, args, parent=ctx, obj=obj)
            sub_ctx.command.invoke(sub_ctx)
        except click.exceptions.MissingParameter as err:
            if err.param:
                send_message(f"Missing Parameter: {err.param.name}")
            else:
                send_message(err.message)
        except click.exceptions.UsageError as err:
            send_message(err.message)
    except BaseException as err:
        logger.exception(f"{cmd_str} failed")
