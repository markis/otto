import asyncio
import tempfile
import urllib.parse
import urllib.request
from collections.abc import Callable, Coroutine
from datetime import datetime
from pathlib import Path
from typing import Final

import requests

from otto.constants import DEFAULT_TIMEOUT, TIMEZONE
from otto.utils.convert import convert_httpstring

HTTP_SUCCESS: Final = 200


def get_now() -> datetime:
    """Return the current time in the TIMEZONE."""
    return datetime.now(tz=TIMEZONE)


def get_time(d: datetime) -> str:
    """Return the time of the datetime object in 12-hour format."""
    return datetime.strftime(d, "%-I:%M")


def get_date(d: datetime) -> str:
    """Return the date of the datetime object in MM/DD format."""
    return datetime.strftime(d, "%m/%d")


def download_image(image_url: str) -> Path:
    """Download an image from a URL and return the file path."""
    if url_path := urllib.parse.urlparse(image_url).path:
        file_ext = Path(url_path).suffix
        file_name = Path(tempfile.mkstemp(file_ext)[1])
        response = requests.get(image_url, stream=True, timeout=DEFAULT_TIMEOUT)
        if response.status_code == HTTP_SUCCESS:
            with Path(file_name).open("wb") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
                    return file_name

    err_msg = f"Failed to download image from {image_url}"
    raise ValueError(err_msg)


def get_url_age(url: str) -> datetime:
    """Get the last modified time of a URL."""
    head_resp = requests.head(url, timeout=10)
    lm = head_resp.headers["last-modified"]
    return convert_httpstring(lm)


async def delete_file(file_path: Path | str) -> None:
    """Delete a file from the file system."""
    Path(file_path).unlink(missing_ok=True)


async def repeat(interval: float, func: Callable[[], Coroutine[None, None, None]]) -> None:
    """Run func every interval seconds.

    If func has not finished before *interval*, will run again
    immediately when the previous iteration finished.
    """
    while True:
        await asyncio.gather(
            func(),
            asyncio.sleep(interval),
        )
