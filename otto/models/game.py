from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import TYPE_CHECKING, Any, Self

from otto.constants import TEAM_NAME
from otto.models.team import Team
from otto.utils import get_now
from otto.utils.convert import convert_isostring

if TYPE_CHECKING:
    from datetime import datetime


@dataclass(slots=True, frozen=True, order=False)
class Game:
    """A game."""

    game_id: str
    game_detail_id: str | None
    game_time: datetime
    season: str
    season_type: str
    week: str
    at_home: bool
    opponent: Team
    home_score: int
    visitor_score: int
    game_phase: str
    venue_name: str
    venue_city: str
    venue_state: str
    networks: list[str]

    data: dict[str, Any]

    def __le__(self: Self, other: Self) -> bool:
        """Return True if this game is less than or equal to the other game."""
        return self.game_time <= other.game_time

    def __lt__(self: Self, other: Self) -> bool:
        """Return True if this game is less than the other game."""
        return self.game_time < other.game_time

    def __ge__(self: Self, other: Self) -> bool:
        """Return True if this game is greater than or equal to the other game."""
        return self.game_time >= other.game_time

    def __gt__(self: Self, other: Self) -> bool:
        """Return True if this game is greater than the other game."""
        return self.game_time > other.game_time

    @property
    def time_until_game(self: Self) -> timedelta:
        """Return the time until the game."""
        return self.game_time - get_now()

    @classmethod
    def from_nfl_dict(cls: type[Game], data: dict[str, Any]) -> Game:
        """Create a game from the NFL API data."""
        assert data

        game_id = data["id"]
        game_detail_id = data.get("gameDetailId")
        assert "gameTime" in data
        game_time = convert_isostring(data["gameTime"])

        week = data["week"]
        assert isinstance(week, dict)
        season = week["season"]
        season_type = week["seasonType"]
        week = week["week"]

        venue = data["venue"]
        assert isinstance(venue, dict)
        venue_name = venue["name"]
        venue_location = venue["location"]
        assert isinstance(venue_location, dict)
        venue_city = venue_location["city"]
        venue_state = venue_location["state"]

        network_channels = data.get("networkChannels")
        assert isinstance(network_channels, dict)
        networks = network_channels["data"]

        visitor_team = data["visitorTeam"]
        home_team = data["homeTeam"]

        at_home = False
        opponent = Team("", "")
        if visitor_team and isinstance(visitor_team, dict) and visitor_team.get("abbr") != TEAM_NAME:
            at_home = True
            opponent = Team(visitor_team.get("abbr", ""), visitor_team.get("nickName", ""))
        elif home_team and isinstance(home_team, dict):
            at_home = False
            opponent = Team(home_team.get("abbr", ""), home_team.get("nickName", ""))

        game_status = data.get("gameStatus")
        assert isinstance(game_status, dict)
        game_phase = game_status.get("phase", "")

        home_score = 0
        home_team_score = data.get("homeTeamScore", {})
        if isinstance(home_team_score, dict):
            home_score = int(home_team_score.get("pointsTotal", 0))

        visitor_score = 0
        visitor_team_score = data.get("visitorTeamScore", {})
        if isinstance(visitor_team_score, dict):
            visitor_score = int(visitor_team_score["pointsTotal"])

        return cls(
            game_id=game_id,
            game_detail_id=game_detail_id,
            game_time=game_time,
            season=season,
            season_type=season_type,
            week=week,
            at_home=at_home,
            opponent=opponent,
            home_score=home_score,
            visitor_score=visitor_score,
            game_phase=game_phase,
            venue_name=venue_name,
            venue_city=venue_city,
            venue_state=venue_state,
            networks=networks,
            data=data,
        )


def get_next_game(games: list[Game], next_opp_delay: float) -> Game | None:
    """Return the next game."""
    next_game = None
    asc_games = sorted(games)
    next_opp_delay_delta = timedelta(seconds=next_opp_delay)
    games_after_delay = [
        game for game in asc_games if game.time_until_game and next_opp_delay_delta < game.time_until_game
    ]
    if games_after_delay:
        next_game = games_after_delay[0]

    return next_game


def get_last_game(games: list[Game], next_opp_delay: float) -> Game | None:
    """Return the last game."""
    next_game = None
    desc_games = sorted(games, reverse=True)
    next_opp_delay_delta = timedelta(seconds=next_opp_delay)
    games_before_delay = [
        game for game in desc_games if game.time_until_game and next_opp_delay_delta > game.time_until_game
    ]
    if games_before_delay:
        next_game = games_before_delay[0]

    return next_game
