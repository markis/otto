from dataclasses import dataclass
from datetime import datetime
from datetime import timedelta
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import TYPE_CHECKING

from otto import TEAM_NAME
from otto.models.team import Team
from otto.utils import convert_isostring
from otto.utils import get_now

if TYPE_CHECKING:
    from _typeshed import SupportsLessThan


@dataclass(frozen=True)
class Game:
    id: str
    game_detail_id: Optional[str]
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
    networks: List[str]

    data: Dict[str, Any]

    @property
    def time_until_game(self) -> timedelta:
        if self.game_time:
            return self.game_time - get_now()
        return datetime(1970, 1, 1) - get_now()

    @classmethod
    def from_nfl_dict(cls, data: Dict[str, Any]) -> "Game":
        assert data

        id = data["id"]
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
        if (
            visitor_team
            and isinstance(visitor_team, dict)
            and visitor_team.get("abbr") != TEAM_NAME
        ):
            at_home = True
            opponent = Team(
                visitor_team.get("abbr", ""), visitor_team.get("nickName", "")
            )
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
            id=id,
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


def _sort_games(game: Game) -> "SupportsLessThan":
    return game.time_until_game


def get_next_game(games: List[Game], next_opp_delay: timedelta) -> Optional[Game]:
    next_game = None
    games.sort(key=_sort_games)
    games_after_delay = [
        game
        for game in games
        if game.time_until_game and next_opp_delay < game.time_until_game
    ]
    if games_after_delay:
        next_game = games_after_delay[0]

    return next_game


def get_last_game(games: List[Game], next_opp_delay: timedelta) -> Optional[Game]:
    next_game = None
    games.sort(key=_sort_games, reverse=True)
    games_before_delay = [
        game
        for game in games
        if game.time_until_game and next_opp_delay > game.time_until_game
    ]
    if games_before_delay:
        next_game = games_before_delay[0]

    return next_game
