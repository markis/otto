import json
import logging
import sys

from collections import deque
from threading import Thread
from typing import Any
from typing import Deque
from typing import Tuple

from flask import Flask
from flask import make_response
from flask import request

from otto import get_reddit
from otto import SUBREDDIT_NAME
from otto.handlers import execute_command
from otto.lib.mod_actions import is_mod
from otto.lib.sendbird_client import send_message


app = Flask(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)
process_list: Deque[str] = deque(maxlen=10)


def done() -> Any:
    return make_response("", 200)


def _parse_request() -> Tuple[str, str, str, str]:
    if request.json:
        msg = request.json.get("message")
        if msg:
            msg_text = msg.get("text")
            msg_id = msg.get("message_id")
        channel = request.json.get("channel")
        if channel:
            channel_url = channel.get("channel_url")
        sender = request.json.get("sender")
        if sender:
            username = sender.get("nickname")
    return msg_id, msg_text, channel_url, username


@app.route("/otto/chat", methods=["POST"])
def chat_handler() -> Any:
    logger.info("handling /otto/chat")
    sr_name = SUBREDDIT_NAME
    reddit = get_reddit()
    msg_id, msg_text, channel_url, username = _parse_request()

    if msg_id in process_list:
        return done()

    if not msg_text or not msg_text.startswith("/"):
        return done()

    if not is_mod(reddit, sr_name, username):
        return done()

    process_list.append(msg_id)

    def _send_message(response: str) -> None:
        send_message(response, channel_url)

    Thread(
        target=execute_command,
        kwargs={
            "cmd_str": "otto " + msg_text,
            "sr_name": sr_name,
            "send_message": _send_message,
            "username": username,
        },
    ).start()

    return done()


@app.errorhandler(404)
def not_found(error: Any) -> Any:
    return make_response(json.dumps({"error": "Not found"}), 404)


def serve_app() -> None:
    from waitress import serve

    logger.info("Serving App")
    serve(app, host="0.0.0.0", port=8001)


if __name__ == "__main__":
    serve_app()
