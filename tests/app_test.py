import re

from time import sleep
from typing import Any
from typing import Callable
from typing import cast
from typing import Optional
from unittest.mock import MagicMock
from unittest.mock import Mock
from unittest.mock import patch

from flask import Flask
from pytest import fixture

from tests.mock import get_mock_reddit
from tests.mock import get_mock_request_get
from tests.mock import SR_RULES
from tests.mock import STRUCTURED_STYLES

# from tests.mock import NFL_API_GAME_RESPONSE
# from tests.mock import NFL_API_STANDINGS_RESPONSE


OTTO_HANDLER_URL = "/otto/chat"
TEST_MOD = "moderator"
TEST_USER = "testuser"
TEST_SR = "brownstest"


class AnyArg(object):
    def __eq__(self, b: object) -> bool:
        return True


class AnyStr(object):
    contains: Optional[str]
    not_contains: Optional[str]

    def __init__(
        self, contains: Optional[str] = None, not_contains: Optional[str] = None
    ) -> None:
        self.contains = contains
        self.not_contains = not_contains

    def __eq__(self, b: object) -> bool:
        if not isinstance(b, str):
            return False
        if self.contains and b.find(self.contains) == -1:
            return False
        if self.not_contains and b.find(self.not_contains) > -1:
            return False
        return True

    def __repr__(self) -> str:
        return f'<AnyStr contains="{self.contains}" not_contains="{self.not_contains}">'


def execute_command(
    cmd_str: Optional[str] = None,
    sr_name: Optional[str] = None,
    send_message: Optional[Callable[[str], None]] = None,
    username: Optional[str] = None,
) -> None:
    from otto.handlers import execute_command as raw_execute_command

    raw_execute_command(
        cmd_str=cmd_str or "",
        sr_name=sr_name or TEST_SR,
        send_message=send_message or MagicMock(),
        username=username or TEST_MOD,
    )


# @fixture(autouse=True)
# def block_requests(monkeypatch) -> None:
#     """ Ensure accidents don't happen """
#     monkeypatch.delattr("urllib.request.urlretrieve")


@patch("otto.get_reddit", new_callable=get_mock_reddit)
@patch("requests.post")
@patch("threading.Thread")
def test_api_handler(
    thread: MagicMock, requests_post: MagicMock, get_reddit: MagicMock
) -> None:
    from otto.app import app

    app.testing = True
    app = cast(Flask, app.test_client())

    test_payload = {
        "channel": {"channel_url": "sendbird_group_channel_123_456"},
        "message": {"message_id": "1", "text": "/help"},
        "sender": {"nickname": "markis"},
    }
    res = app.post(OTTO_HANDLER_URL, json=test_payload)

    assert res.status_code == 200


@patch("otto.get_reddit", new_callable=get_mock_reddit)
@patch("requests.post")
def test_help(requests_post: MagicMock, get_reddit: MagicMock) -> None:

    send_message = MagicMock()

    execute_command(cmd_str="otto /help", send_message=send_message)

    # /help should return all the commands, but shouldn't show the options for the commands
    send_message.assert_called_once_with(
        AnyStr(
            contains="Otto Grahaminator - ultimate moderator of r/Browns\nCommands:",
            not_contains="Options:",
        )
    )


@patch("otto.get_reddit", new_callable=get_mock_reddit)
@patch("requests.post")
def test_ban_user(requests_post: MagicMock, get_reddit: MagicMock) -> None:
    send_message = MagicMock()
    duration = 22
    rule = 1
    rule_short = SR_RULES[rule - 1]["short_name"]

    execute_command(
        cmd_str=f"otto /ban -u {TEST_USER} -d {duration} -r {rule}",
        send_message=send_message,
    )

    get_reddit().subreddit(TEST_SR).banned.add.assert_called_once_with(
        TEST_USER, ban_message=None, ban_reason=rule_short, duration=duration, note=None
    )
    send_message.assert_called_once_with(
        f'u/{TEST_USER} has been banned for {duration} days for violating "{rule_short}"'
    )


@patch("otto.get_reddit", new_callable=get_mock_reddit)
@patch("requests.post")
def test_compliment(requests_post: MagicMock, get_reddit: MagicMock) -> None:
    send_message = MagicMock()
    execute_command(cmd_str=f"otto /compliment", send_message=send_message)
    send_message.assert_called_with(AnyStr(contains=TEST_MOD))

    execute_command(
        cmd_str=f"otto /compliment -u {TEST_USER}", send_message=send_message
    )
    send_message.assert_called_with(AnyStr(contains=TEST_USER))


@patch("otto.get_reddit", new_callable=get_mock_reddit)
@patch("requests.post")
def test_enable_text_posts(requests_post: MagicMock, get_reddit: MagicMock) -> None:
    send_message = MagicMock()
    execute_command(cmd_str=f"otto /enable_text_posts", send_message=send_message)
    get_reddit().subreddit(TEST_SR).mod.update.assert_called_with(link_type="any")


@patch("otto.get_reddit", new_callable=get_mock_reddit)
@patch("requests.post")
def test_disable_text_posts(requests_post: MagicMock, get_reddit: MagicMock) -> None:
    send_message = MagicMock()
    execute_command(cmd_str=f"otto /disable_text_posts", send_message=send_message)
    get_reddit().subreddit(TEST_SR).mod.update.assert_called_with(link_type="link")


@patch("otto.get_reddit", new_callable=get_mock_reddit)
@patch("requests.post")
@patch("urllib.request.urlretrieve")
def test_sidebar(
    urlretrieve: MagicMock, requests_post: MagicMock, get_reddit: MagicMock
) -> None:
    send_message = MagicMock()
    execute_command(
        cmd_str=f"otto /sidebar http://www.redit.com/image", send_message=send_message
    )


@patch("otto.get_reddit", new_callable=get_mock_reddit)
@patch("requests.get", new_callable=get_mock_request_get)
@patch("requests.post")
@patch("requests.head")
def test_game_day_thread(
    requests_head: MagicMock,
    requests_post: MagicMock,
    requests_get: MagicMock,
    get_reddit: MagicMock,
) -> None:
    requests_post.side_effect = [
        MagicMock(json=MagicMock(return_value={"access_token": "123"}))
    ]
    send_message = MagicMock()
    execute_command(cmd_str=f"otto /game_day_thread", send_message=send_message)

    # get_reddit().post.assert_called()
    # get_reddit().subreddit().submit.assert_called()
    # get_reddit().submission().mod.remove.assert_called()
    # send_message.assert_called()
