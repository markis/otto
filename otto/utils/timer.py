from __future__ import annotations

import time
from typing import Any


class Timer:
    """Context manager for timing code blocks"""

    _start: float
    _end: float
    _elapsed: float
    __slots__: tuple[str, ...] = tuple()

    @property
    def elapsed(self) -> float:
        return self.__elapsed

    def __enter__(self) -> Timer:
        self.__start
        return self

    def __exit__(self, *_: Any) -> None:
        self.stop()

    def start(self) -> None:
        self.__start = time.time()

    def stop(self) -> None:
        self.__end = time.time()
        self.__elapsed = self.__end - self.__start
