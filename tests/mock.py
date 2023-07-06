import inspect
import json
import os
from collections.abc import Callable
from typing import Any
from unittest.mock import Mock

from asyncpraw.reddit import Reddit

OTTO_CONFIG_PATH = "ottograhaminator"
OTTO_CONFIG = """
enable_automatic_sidebar_scores: yes
enable_automatic_downvotes: yes
delay_downvotes: -24hr
"""

OLD_SIDEBAR = """

----

#2021 OPPONENTS

DATE|OPPONENT|TIME|
|:---:|:--:|:---:|
|9/8|[](/r/tennesseetitans) (TEN)|L 43-13|
|12/29|@ [](/r/bengals) (CIN)|1:00|
----

"""

OLD_CSS = """
/* Sidebar Pic */
h1.redditname {
  width: 300px;
  height: 400px;
  background-image: url("%%sidebar%%") !important;
  background-repeat: no-repeat;
  background-position-x: center;
  background-position-y: center;
  -webkit-background-size: cover;
  -moz-background-size: cover;
  -o-background-size: cover;
  background-size: cover;
  padding: 0 !important;
  margin: 0px !important;
  margin-top: 6px !important;
  margin-left: 0px !important;
  margin-bottom: 15px !important;
  text-indent: -3000px;
}

/* Custom Team Downvotes */
.arrow.down {
  background-image: url("%%teamsmallfade%%");
  background-position: 0px -45px;
}

.arrow.downmod {
  background-image: url("%%teamsmall%%");
  background-position: 0px -45px;
}
"""

STRUCTURED_STYLES = {
    "data": {
        "style": {
            "postDownvoteIconActive": "http://reddit.com",
            "postDownvoteIconInactive": "http://reddit.com",
        }
    }
}

SR_RULES = [{"short_name": "No Personal Attacks or Flame Baiting"}]

mock_reddit = Mock(
    subreddit=Mock(
        return_value=Mock(
            mod=Mock(settings=Mock(return_value={"description": OLD_SIDEBAR})),
            moderator=Mock(return_value=Mock(children=[Mock(name="markis")])),
            rules=Mock(return_value={"rules": SR_RULES}),
            stylesheet=Mock(return_value=Mock(stylesheet=OLD_CSS)),
            widgets=Mock(
                sidebar=[
                    Mock(shortName="Preseason Opponents", text=""),
                    Mock(shortName="2021 Opponents", text=""),
                    Mock(shortName="AFCN Standings", text=""),
                ]
            ),
            wiki={OTTO_CONFIG_PATH: Mock(content_md=OTTO_CONFIG)},
        )
    )
)


def get_mock_reddit() -> Callable[[], Reddit]:
    def get_reddit() -> Reddit:
        return mock_reddit

    return get_reddit


def get_mock_request_get() -> Callable[[], Any]:
    def get_mock_data(name: str) -> Any:
        f = open(f"{os.getcwd()}/tests/data/{name}.json")
        obj = json.load(f)
        f.close()
        return Mock(json=Mock(return_value=obj))

    def request_get(*args: list[Any], **kwargs: dict[Any, Any]) -> Any:
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        caller = calframe[2][3]
        return get_mock_data(caller)

    return request_get
