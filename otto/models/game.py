from datetime import datetime
from datetime import timedelta
from typing import Dict
from typing import List
from typing import Optional

from otto import TEAM_NAME
from otto.models.team import Team
from otto.utils import convert_isostring
from otto.utils import get_now


class Game:
    id: str
    game_detail_id: Optional[str]
    game_time: datetime
    season: str
    season_type: str
    week: str
    at_home: bool
    opponent: Team
    home_score: str
    visitor_score: str
    game_phase: str
    venue_name: str
    venue_city: str
    venue_state: str
    networks: List[str]

    data: Dict[str, str]

    @property
    def time_until_game(self) -> Optional[timedelta]:
        if self.game_time:
            return self.game_time - get_now()
        return None

    def __init__(self, data: Dict[str, str]):
        assert data
        self.data = data

        self.id = data["id"]
        self.game_detail_id = data.get("gameDetailId")
        assert "gameTime" in data
        self.game_time = convert_isostring(data["gameTime"])

        week = data["week"]
        assert isinstance(week, dict)
        self.season = week["season"]
        self.season_type = week["seasonType"]
        self.week = week["week"]

        venue = data["venue"]
        assert isinstance(venue, dict)
        self.venue_name = venue["name"]
        venue_location = venue["location"]
        assert isinstance(venue_location, dict)
        self.venue_city = venue_location["city"]
        self.venue_state = venue_location["state"]

        network_channels = data.get("networkChannels")
        assert isinstance(network_channels, dict)
        self.networks = network_channels["data"]

        visitor_team = data["visitorTeam"]
        home_team = data["homeTeam"]

        if (
            visitor_team
            and isinstance(visitor_team, dict)
            and visitor_team.get("abbr") != TEAM_NAME
        ):
            self.at_home = True
            self.opponent = Team(visitor_team.get("abbr"), visitor_team.get("nickName"))
        elif home_team and isinstance(home_team, dict):
            self.at_home = False
            self.opponent = Team(home_team.get("abbr"), home_team.get("nickName"))

        game_status = data.get("gameStatus")
        assert isinstance(game_status, dict)
        self.game_phase = game_status.get("phase")

        home_team_score = data.get("homeTeamScore")
        if isinstance(home_team_score, dict):
            self.home_score = int(home_team_score["pointsTotal"])

        visitor_team_score = data.get("visitorTeamScore")
        if isinstance(visitor_team_score, dict):
            self.visitor_score = int(visitor_team_score["pointsTotal"])


def _sort_games(game: Game) -> Optional[timedelta]:
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
