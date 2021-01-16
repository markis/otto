import asyncio
import json
import logging
import sys
import zlib

from collections import deque
from pprint import pprint
from typing import Any
from typing import Deque
from typing import Dict
from typing import List
from typing import Tuple
from typing import Union

import nest_asyncio

from discord import Client
from discord import Message

from otto import DISCORD_TOKEN
from otto import SUBREDDIT_NAME
from otto.handlers import execute_command

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger("otto.discord")
# Z_SYNC_FLUSH suffix
ZLIB_SUFFIX = b"\x00\x00\xff\xff"


class DiscordClient(Client):  # type: ignore
    msg_buffer = bytearray()
    inflator = zlib.decompressobj()
    process_list: Deque[str] = deque(maxlen=10)

    def _parse_request(self, message: Message) -> Tuple[str, str, str, str]:
        if message:
            msg_id = message.id
            msg_text = message.content
            channel_url = message.channel
            username = message.author.name

        return msg_id, msg_text, channel_url, username

    def _parse_interaction(self, message: Dict[str, Any]) -> Tuple[str, str, str, str]:
        if message:
            message_data = message["d"]
            if message_data:
                msg_id = message_data["id"]
                channel_id = message_data["channel_id"]
                username = message_data["member"]["user"]["username"]

                data = message_data["data"]
                msg_text = f"/{data['name']}"
                for option in data.get("options", []):
                    msg_text += f" --{option['name']}=\"{option['value']}\""

        return msg_id, msg_text, channel_id, username

    def asyncio_run(self, future: Any, as_task: bool = True) -> Any:
        """
        A better implementation of `asyncio.run`.

        :param future: A future or task or call of an async method.
        :param as_task: Forces the future to be scheduled as task (needed for e.g. aiohttp).
        """

        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:  # no event loop running:
            loop = asyncio.new_event_loop()
            return loop.run_until_complete(self._to_task(future, as_task, loop))
        else:
            nest_asyncio.apply(loop)
            return asyncio.run_coroutine_threadsafe(future, loop)

    def _to_task(self, future: Any, as_task: bool, loop: Any) -> Any:
        if not as_task or isinstance(future, asyncio.Task):
            return future
        return loop.create_task(future)

    async def on_socket_raw_receive(self, msg_bytes: bytes) -> None:
        logger.info("on_socket_raw_receive")

        if type(msg_bytes) is bytes:
            self.msg_buffer.extend(msg_bytes)

        if len(msg_bytes) < 4 or msg_bytes[-4:] != ZLIB_SUFFIX:
            return

        try:
            msg_bytes = self.inflator.decompress(self.msg_buffer)
            msg_str = msg_bytes.decode("utf-8")
            self.msg_buffer = bytearray()
        except BaseException as ex:
            logger.error("Error decompressing and decoding buffer", exc_info=ex)
            sys.exit("Error decompressing and decoding buffer")

        msg = json.loads(msg_str)
        if msg.get("t") == "INTERACTION_CREATE":
            msg_id, msg_text, channel_id, username = self._parse_interaction(msg)

            channel = client.get_channel(channel_id)
            if not channel:
                channel = await client.fetch_channel(channel_id)

            def _send_message(response: str) -> None:
                self.asyncio_run(channel.send(response))

            execute_command(
                cmd_str=f"otto {msg_text}",
                sr_name=SUBREDDIT_NAME,
                send_message=_send_message,
                username=username,
            )

    async def on_message(self, message: Message) -> None:
        logger.info("on_message")
        sr_name = SUBREDDIT_NAME
        msg_id, msg_text, channel_url, username = self._parse_request(message)
        logger.debug(f"{msg_id}, {msg_text}")

        if message.author == client.user:
            return

        if msg_id in self.process_list:
            return

        if not msg_text or not msg_text.startswith("/"):
            return

        self.process_list.append(msg_id)

        def _send_message(response: str) -> None:
            self.asyncio_run(message.channel.send(response))

        execute_command(
            cmd_str=f"otto {msg_text}",
            sr_name=sr_name,
            send_message=_send_message,
            username=username,
        )


def update_slash_commands() -> None:
    import click
    import requests
    from otto.handlers import otto

    app_id = 792417327437316126
    server_id = 783727217179623435

    url = (
        f"https://discord.com/api/v8/applications/{app_id}/guilds/{server_id}/commands"
    )

    def _generate_command(command: click.Command) -> Dict[str, Any]:
        name = (command.name or "")[1:]
        help = (command.help or name or "")[:100]
        return {
            "name": name,
            "description": help,
            "options": _generate_options(command),
        }

    def _generate_options(command: click.Command) -> List[Dict[str, Any]]:
        return [
            {
                "name": param.name,
                "description": getattr(param, "help", param.name)[:100],
                "type": _get_type(param),
                "required": param.required,
            }
            for param in command.params
        ]

    def _get_type(param: Union[click.Argument, click.Parameter]) -> int:
        if param.type == click.INT:
            return 4
        elif isinstance(param.type, click.IntRange):
            return 4

        return 3

    # For authorization, you can use either your bot token
    headers = {"Authorization": f"Bot {DISCORD_TOKEN}"}

    for cmd in otto.commands:
        json = _generate_command(otto.commands[cmd])
        r = requests.post(url, headers=headers, json=json)
        if r.status_code != 200:
            pprint(json)
            print(r.json())


if __name__ == "__main__":
    update_slash_commands()
    client = DiscordClient()
    client.run(DISCORD_TOKEN)
