from datetime import datetime, timedelta

from otto.constants import TIMEZONE, TRUTHY_VALUES


def convert_to_bool(val: str | int | bool | None) -> bool:
    """Convert a value to a bool."""
    return val in (1, True) or (type(val) == str and val.lower() in TRUTHY_VALUES)


def convert_to_int(val: str | int | bool | None) -> int:
    """Convert a value to an int."""
    if type(val) == int:
        return val
    if type(val) == str and val.isdigit():
        return int(val)
    if type(val) == str and val.lower() in TRUTHY_VALUES:
        return 1
    if type(val) == bool and val is True:
        return 1
    return 0


def convert_to_timedelta(val: str | int | bool | None) -> timedelta:
    """Convert a value to a timedelta."""
    if type(val) == int:
        return timedelta(seconds=val)
    if type(val) == str:
        from pytimeparse.timeparse import timeparse

        val_time = timeparse(val)
        assert val_time is not None
        return timedelta(seconds=val_time)
    if type(val) == bool and val is True:
        return timedelta(seconds=1)
    return timedelta(seconds=0)


def convert_isostring(dt: str) -> datetime:
    """Convert an ISO 8601 string to a datetime object."""
    return datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S.%f%z").astimezone(TIMEZONE)


def convert_tzstring(dt: str) -> datetime:
    """Convert a datetime string with a timezone to a datetime object."""
    return datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S%z").astimezone(TIMEZONE)


def convert_httpstring(dt: str) -> datetime:
    """Convert an HTTP datetime string to a datetime object."""
    return datetime.strptime(dt, "%a, %d %b %Y %H:%M:%S %Z").astimezone(TIMEZONE)
