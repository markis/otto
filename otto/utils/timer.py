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
        return self._elapsed

    def __enter__(self) -> Timer:
        self._start
        return self

    def __exit__(self, *_: Any) -> None:
        self.stop()

    def start(self) -> None:
        self._start = time.time()

    def stop(self) -> None:
        self._end = time.time()
        self._elapsed = self._end - self._start
