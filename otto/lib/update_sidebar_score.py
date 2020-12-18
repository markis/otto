import inspect
import re

from typing import Any
from typing import List

import praw
import tinycss2

from otto import get_reddit
from otto import SUBREDDIT_NAME
from otto.config import Config
from otto.errors import SidebarBackgroundImageError
from otto.lib.nfl_client import NFLClient
from otto.models.game import Game
from otto.models.record import Record
from otto.models.team import get_name
from otto.models.team import get_subreddit
from otto.utils import get_date
from otto.utils import get_time

spacer = "&nbsp;&nbsp;&nbsp;"
season_table_header = f"""
{spacer}**Date**{spacer}||**Opponent**|{spacer}**Time**{spacer}
:--:|:--:|:--|:--:
"""
standings_table_header = """
||**W-L**|**Home**|**Away**|**Div**|**Streak**|
|:---:|:--:|:--:|:--:|:--:|:--:|
"""

preseason_regex = re.compile(
    r"""(
#PRESEASON OPPONENTS\s*
DATE\|OPPONENT\|TIME\|\s*
\|:---:\|:--:\|:---:\|
)(.|\s)*?(
-{3,})""",
    re.DOTALL | re.IGNORECASE,
)

regular_regex = re.compile(
    r"""(
#\d\d\d\d OPPONENTS\s*
DATE\|\|OPPONENT\|TIME\|\s*
\|:---:\|:--:\|:--\|:---:\|
)(.|\s)*?(
-{3,})""",
    re.DOTALL | re.IGNORECASE,
)

standings_regex = re.compile(
    r"""(
#AFCN Standings\s*
\|\|\*\*W-L\*\*\|\*\*Home\*\*\|\*\*Away\*\*\|\*\*Div\*\*\|\*\*Streak\*\*\|\s*
\|:---:\|:--:\|:--:\|:--:\|:--:\|:--:\|
)(.|\s)*?(
-{3,})""",
    re.DOTALL | re.IGNORECASE,
)


def get_game_outcome(game: Game) -> str:
    outcome = get_time(game.game_time)
    if game.game_phase != "PREGAME":
        if game.at_home:
            if game.home_score > game.visitor_score:
                outcome = f"W {game.home_score}-{game.visitor_score}"
            elif game.home_score < game.visitor_score:
                outcome = f"L {game.home_score}-{game.visitor_score}"
            else:
                outcome = f"T {game.home_score}-{game.visitor_score}"
        else:
            if game.visitor_score > game.home_score:
                outcome = f"W {game.visitor_score}-{game.home_score}"
            elif game.visitor_score < game.home_score:
                outcome = f"L {game.visitor_score}-{game.home_score}"
            else:
                outcome = f"T {game.visitor_score}-{game.home_score}"
    return outcome


def _get_seasons(games: List[Game]) -> Any:
    preseason = list()
    regular = list()
    last_game_date = None
    for game in games:
        date = get_date(game.game_time)
        at = not game.at_home and "@ " or "vs"
        sub = get_subreddit(game.opponent.abbr)
        abbr = game.opponent.abbr
        outcome = get_game_outcome(game)
        name = get_name(abbr)

        time_since_last_game = last_game_date and game.game_time - last_game_date
        last_game_date = game.game_time

        if time_since_last_game and time_since_last_game.days > 11:
            regular.append(f"|BYE|||")

        if game.season_type == "PRE":
            preseason.append(f"|{date}|{at}|[]({sub}) {abbr}|{outcome}|")
        if game.season_type == "REG":
            # date = get_date_special(game.game_time)
            regular.append(f"|{date}|{at}|**[{name}]({sub})**|{outcome}|")

    return {"preseason": "\n".join(preseason), "regular": "\n".join(regular)}


def _maybe_add_tie(tie: int) -> str:
    if tie > 0:
        return f"-{tie}"
    else:
        return ""


def _get_records(records: List[Record]) -> str:
    standings = list()
    for record in records:
        abbr = record.abbr
        sub = get_subreddit(record.abbr)
        streak = record.streak
        overall = f"{record.win}-{record.loss}{_maybe_add_tie(record.tie)}"
        home = f"{record.home_win}-{record.home_loss}{_maybe_add_tie(record.home_tie)}"
        away = f"{record.road_win}-{record.road_loss}{_maybe_add_tie(record.road_tie)}"
        div = f"{record.division_win}-{record.division_loss}{_maybe_add_tie(record.division_tie)}"

        standings.append(f"|[]({sub})({abbr})|{overall}|{home}|{away}|{div}|{streak}|")

    return "\n".join(standings)


def update_sidebar_score(
    config: Config,
    reddit: praw.Reddit,
    sr_name: str,
    games: List[Game],
    records: List[Record],
) -> None:
    seasons = _get_seasons(games)
    standings = _get_records(records)

    # Update old reddit
    sr_browns = reddit.subreddit(sr_name)
    settings = sr_browns.mod.settings()

    desc = settings["description"]
    new_desc = re.sub(standings_regex, r"\1" + standings + r"\3", desc, 1)
    new_desc = re.sub(
        preseason_regex, r"\1" + seasons["preseason"] + r"\3", new_desc, 1
    )
    new_desc = re.sub(regular_regex, r"\1" + seasons["regular"] + r"\3", new_desc, 1)

    if desc != new_desc:
        sr_browns.mod.update(description=new_desc)

    # Update new reddit
    widgets = sr_browns.widgets

    preseason = season_table_header + seasons["preseason"]
    regular = season_table_header + seasons["regular"]
    standings = standings_table_header + standings
    for widget in widgets.sidebar:
        if widget.shortName == "Preseason Opponents":
            if widget.text != preseason:
                widget.mod.update(text=preseason)
        elif widget.shortName == "2020 Opponents":
            if widget.text != regular:
                widget.mod.update(text=regular)
        elif widget.shortName == "AFCN Standings":
            if widget.text != standings:
                widget.mod.update(text=standings)
