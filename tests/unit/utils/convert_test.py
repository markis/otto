from datetime import datetime, timedelta

import pytest

from otto.constants import TIMEZONE
from otto.utils.convert import (
    convert_httpstring,
    convert_isostring,
    convert_to_bool,
    convert_to_int,
    convert_to_timedelta,
    convert_tzstring,
)


@pytest.mark.parametrize(
    ("val", "expected"),
    [
        ("1", True),
        ("0", False),
        ("true", True),
        ("false", False),
        ("yes", True),
        ("no", False),
        (1, True),
        (0, False),
        (True, True),
        (False, False),
        (None, False),
    ],
)
def test_convert_to_bool(*, val: str | int | bool | None, expected: bool) -> None:
    """Test convert_to_bool."""
    assert convert_to_bool(val) == expected


@pytest.mark.parametrize(
    ("val", "expected"),
    [
        ("1", 1),
        ("0", 0),
        ("true", 1),
        ("false", 0),
        ("yes", 1),
        ("no", 0),
        (1, 1),
        (0, 0),
        (True, 1),
        (False, 0),
        (None, 0),
    ],
)
def test_convert_to_int(*, val: str | int | bool | None, expected: bool) -> None:
    """Test convert_to_int."""
    assert convert_to_int(val) == expected


@pytest.mark.parametrize(
    ("val", "expected"),
    [
        ("-24hr", timedelta(days=-1)),
        ("-4hr", timedelta(hours=-4)),
        ("-1hr", timedelta(hours=-1)),
        ("-30min", timedelta(minutes=-30)),
        ("-1min", timedelta(minutes=-1)),
        ("-30sec", timedelta(seconds=-30)),
        ("-1sec", timedelta(seconds=-1)),
        ("0sec", timedelta(seconds=0)),
        ("1sec", timedelta(seconds=1)),
        ("30sec", timedelta(seconds=30)),
        ("1min", timedelta(minutes=1)),
        ("30min", timedelta(minutes=30)),
        ("1hr", timedelta(hours=1)),
        ("4hr", timedelta(hours=4)),
        ("24hr", timedelta(days=1)),
        ("1day", timedelta(days=1)),
        ("1day1hr", timedelta(days=1, hours=1)),
        ("1day1hr1min", timedelta(days=1, hours=1, minutes=1)),
        ("1day1hr1min1sec", timedelta(days=1, hours=1, minutes=1, seconds=1)),
        ("1day1min", timedelta(days=1, minutes=1)),
        (1, timedelta(seconds=1)),
        (0, timedelta(seconds=0)),
        (True, timedelta(seconds=1)),
        (object(), timedelta(seconds=0)),
    ],
)
def test_convert_to_timedelta(*, val: str | int | bool | None, expected: timedelta) -> None:
    """Test convert_to_timedelta."""
    assert convert_to_timedelta(val) == expected


@pytest.mark.parametrize(
    ("val", "expected"),
    [
        ("2021-01-01T00:00:00.000000+00:00", datetime(2021, 1, 1, 0, 0, 0, 0, tzinfo=TIMEZONE)),
        ("2021-01-01T00:00:00.000000Z", datetime(2021, 1, 1, 0, 0, 0, 0, tzinfo=TIMEZONE)),
        ("2021-01-01T12:30:56.123456Z", datetime(2021, 1, 1, 12, 30, 56, 123456, tzinfo=TIMEZONE)),
    ],
)
def test_convert_isostring(*, val: str, expected: datetime) -> None:
    """Test convert_isostring."""
    assert convert_isostring(val) == expected


@pytest.mark.parametrize(
    ("val", "expected"),
    [
        ("2021-01-01T00:00:00+00:00", datetime(2021, 1, 1, 0, 0, 0, 0, tzinfo=TIMEZONE)),
        ("2021-01-01T00:00:00Z", datetime(2021, 1, 1, 0, 0, 0, 0, tzinfo=TIMEZONE)),
        ("2021-01-01T12:30:56Z", datetime(2021, 1, 1, 12, 30, 56, 0, tzinfo=TIMEZONE)),
    ],
)
def test_convert_tzstring(*, val: str, expected: datetime) -> None:
    """Test convert_tzstring."""
    assert convert_tzstring(val) == expected


@pytest.mark.parametrize(
    ("val", "expected"),
    [
        ("Fri, 1 Jan 2021 00:00:00 UTC", datetime(2021, 1, 1, 5, 0, 0, 0, tzinfo=TIMEZONE)),
        ("Fri, 1 Jan 2021 05:00:00 UTC", datetime(2021, 1, 1, 10, 0, 0, 0, tzinfo=TIMEZONE)),
        ("Fri, 1 Jan 2021 10:00:00 UTC", datetime(2021, 1, 1, 15, 0, 0, 0, tzinfo=TIMEZONE)),
        ("Fri, 1 Jan 2021 15:00:00 UTC", datetime(2021, 1, 1, 20, 0, 0, 0, tzinfo=TIMEZONE)),
        ("Fri, 1 Jan 2021 01:00:00 UTC", datetime(2021, 1, 1, 6, 0, 0, 0, tzinfo=TIMEZONE)),
    ],
)
def test_convert_httpstring(*, val: str, expected: datetime) -> None:
    """Test convert_httpstring."""
    assert convert_httpstring(val) == expected
