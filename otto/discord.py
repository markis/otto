import logging
import sys

from collections import deque
from threading import Thread
from typing import Deque
from typing import Tuple

from discord import Client
from discord import Message
from otto import DISCORD_TOKEN
from otto import SUBREDDIT_NAME
from otto.handlers import execute_command

client = Client()
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)
process_list: Deque[str] = deque(maxlen=10)


def _parse_request(message: Message) -> Tuple[str, str, str, str]:
    if message:
        msg_id = message.id
        msg_text = message.content
        channel_url = message.channel
        username = message.author.name

    return msg_id, msg_text, channel_url, username


@client.event
async def on_message(message: Message):
    logger.info("handling discord message")
    sr_name = SUBREDDIT_NAME
    msg_id, msg_text, channel_url, username = _parse_request(message)
    logger.debug(f"{msg_id}, {msg_text}")

    if message.author == client.user:
        return

    if msg_id in process_list:
        return

    if not msg_text or not msg_text.startswith("/"):
        return

    process_list.append(msg_id)

    def _send_message(response: str) -> None:
        yield from message.channel.send(response)

    Thread(
        target=execute_command,
        kwargs={
            "cmd_str": "otto " + msg_text,
            "sr_name": sr_name,
            "send_message": _send_message,
            "username": username,
        },
    ).start()


if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
