import typing


SendMessage = typing.Callable[[str], typing.Coroutine[None, None, None]]
