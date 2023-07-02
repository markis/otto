import typing

SendMessage = typing.Callable[[str], typing.Coroutine[typing.Any, typing.Any, None]]
