import asyncio
import logging
import sys

from collections import deque
from concurrent.futures import Future
from typing import Any
from typing import Deque
from typing import Tuple

import nest_asyncio

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


def asyncio_run(future: Any, as_task: bool = True) -> Future[Any]:
    """
    A better implementation of `asyncio.run`.

    :param future: A future or task or call of an async method.
    :param as_task: Forces the future to be scheduled as task (needed for e.g. aiohttp).
    """

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # no event loop running:
        loop = asyncio.new_event_loop()
        return loop.run_until_complete(_to_task(future, as_task, loop))
    else:
        nest_asyncio.apply(loop)
        return asyncio.run_coroutine_threadsafe(future, loop)


def _to_task(future: Any, as_task: bool, loop: Any) -> Any:
    if not as_task or isinstance(future, asyncio.Task):
        return future
    return loop.create_task(future)


@client.event
async def on_message(message: Message) -> None:
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
        asyncio_run(message.channel.send(response))

    execute_command(
        cmd_str=f"otto {msg_text}",
        sr_name=sr_name,
        send_message=_send_message,
        username=username,
    )


if __name__ == "__main__":
    client.run(DISCORD_TOKEN)
