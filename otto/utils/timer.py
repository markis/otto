from __future__ import annotations

import time
from typing import Self


class Timer:
    """Context manager for timing code blocks."""

    _start: float
    _end: float
    _elapsed: float
    __slots__: tuple[str, ...] = ()

    @property
    def elapsed(self: Self) -> float:
        """Return the elapsed time."""
        return self._elapsed

    def __enter__(self: Self) -> Timer:
        """Start the timer."""
        self.start()
        return self

    def __exit__(self: Self, *_: object) -> None:
        """Stop the timer."""
        self.stop()

    def start(self: Self) -> None:
        """Start the timer."""
        self._start = time.time()

    def stop(self: Self) -> None:
        """Stop the timer."""
        self._end = time.time()
        self._elapsed = self._end - self._start
