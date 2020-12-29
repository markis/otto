import os
import tempfile
import urllib.parse
import urllib.request

from datetime import datetime

import pytz
import requests


TIMEZONE = pytz.timezone("America/New_York")


def get_now() -> datetime:
    return datetime.now(tz=TIMEZONE)


def get_time(d: datetime) -> str:
    return datetime.strftime(d, "%-I:%M")


def get_date(d: datetime) -> str:
    return datetime.strftime(d, "%m/%d")


# def get_date_special(d: datetime) -> str:
#     date_str = get_date(d)
#     weekday = d.weekday()
#     hour = d.hour

#     if weekday == 0:
#         date_str = date_str + " (Mon)"
#     if weekday == 3:
#         date_str = date_str + " (Thurs)"
#     if weekday == 6 and hour == 20:
#         date_str = date_str + " (Sun Night)"

#     return date_str


def convert_isostring(dt: str) -> datetime:
    d = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S.%f%z")
    d = d.astimezone(TIMEZONE)
    return d


def convert_tzstring(dt: str) -> datetime:
    d = datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S%z")
    d = d.astimezone(TIMEZONE)
    return d


def convert_httpstring(dt: str) -> datetime:
    d = datetime.strptime(dt, "%a, %d %b %Y %H:%M:%S %Z")
    d = d.astimezone(TIMEZONE)
    return d


def download_image(image_url: str) -> str:
    url_path = urllib.parse.urlparse(image_url).path
    file_ext = os.path.splitext(url_path)[1]
    file_name = tempfile.mkstemp(file_ext)[1]
    urllib.request.urlretrieve(image_url, filename=file_name)
    return file_name


def get_url_age(url: str) -> datetime:
    head_resp = requests.head(url)
    lm = head_resp.headers["last-modified"]
    return convert_httpstring(lm)


def delete_file(file_path: str) -> None:
    os.remove(file_path)
