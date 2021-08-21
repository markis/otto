import typing

from discord_slash.model import SlashMessage


SendMessage = typing.Callable[
    [str], typing.Coroutine[typing.Any, typing.Any, SlashMessage]
]
