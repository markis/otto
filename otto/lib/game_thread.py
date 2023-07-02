import asyncio
from datetime import datetime, timedelta

from otto import TEAM_NAME
from otto.lib.nfl_client import NFLClient
from otto.lib.weather_client import WeatherClient
from otto.models.game import get_next_game
from otto.models.team import get_location, get_subreddit
from otto.types import SendMessage
from otto.utils import get_time

weather_client = WeatherClient()

standings_header = """
|Team|Record|Home|Road|Division|Conference|Streak|
|:-----:|:-----:|:------:|:------:|:------:|:------:|:------:|
"""


def _maybe_add_tie(tie: int) -> str:
    if tie > 0:
        return f"-{tie}"
    else:
        return ""


def _get_standings_table(nfl_client: NFLClient, team: str, opponent: str) -> str:
    records = nfl_client.get_standings(teams=[team, opponent])

    standings_rows = []
    for record in records:
        standings_rows.append(
            " ".join(
                f"""|
                {record.abbr} |
                {record.win}-{record.loss}{_maybe_add_tie(record.tie)} |
                {record.home_win}-{record.home_loss}{_maybe_add_tie(record.home_tie)} |
                {record.road_win}-{record.road_loss}{_maybe_add_tie(record.road_tie)} |
                {record.division_win}-{record.division_loss}{_maybe_add_tie(record.division_tie)} |
                {record.conference_win}-{record.conference_loss}{_maybe_add_tie(record.conference_tie)} |
                {record.streak} |
            """.split()
            )
        )
    return standings_header + "\n".join(standings_rows)


def _get_weather(team_abbr: str, game_time: datetime) -> str:
    lat, lon = get_location(team_abbr)
    try:
        w = weather_client.get_weather(lat, lon, game_time)
        if w:
            return f"{w.temperature}° - {w.forecast} - Wind {w.wind_direction} {w.wind_speed}"
    except BaseException:
        pass

    return ""


async def _default_send_message(msg: str) -> None:
    """Default send_message will just print to console"""
    print(msg)


async def generate_game_thread(
    send_message: SendMessage = _default_send_message,
) -> None:
    nfl_client = NFLClient()
    games = nfl_client.get_scores()

    next_game = get_next_game(games, timedelta())

    assert next_game
    team_abbr = TEAM_NAME
    team_name = "Browns"
    next_team = next_game.opponent
    next_abbr = next_team.abbr
    next_location_abbr = team_abbr if next_game.at_home else next_abbr

    # game_data = nfl_client.get_game(next_game.id)
    # game_detail_id = game_data["gameDetailId"]
    # details = nfl_client.get_game_details(game_detail_id)

    standings_table = _get_standings_table(nfl_client, team_abbr, next_abbr)
    weather_forecast = _get_weather(next_location_abbr, next_game.game_time)

    team_subreddit = get_subreddit(team_abbr)
    next_subreddit = get_subreddit(next_abbr)

    team_pass_lead = nfl_client.get_stat_leader("passing.yards", team_abbr)
    team_rush_lead = nfl_client.get_stat_leader("rushing.yards", team_abbr)
    team_rec_lead = nfl_client.get_stat_leader("receiving.yards", team_abbr)
    team_tack_lead = nfl_client.get_stat_leader("defensive.combineTackles", team_abbr)
    team_int_lead = nfl_client.get_stat_leader("defensive.interceptions", team_abbr)
    team_sack_lead = nfl_client.get_stat_leader("defensive.sacks", team_abbr)

    next_pass_lead = nfl_client.get_stat_leader("passing.yards", next_abbr)
    next_rush_lead = nfl_client.get_stat_leader("rushing.yards", next_abbr)
    next_rec_lead = nfl_client.get_stat_leader("receiving.yards", next_abbr)
    next_tack_lead = nfl_client.get_stat_leader("defensive.combineTackles", next_abbr)
    next_int_lead = nfl_client.get_stat_leader("defensive.interceptions", next_abbr)
    next_sack_lead = nfl_client.get_stat_leader("defensive.sacks", next_abbr)

    title = f"[GAME DAY THREAD] {team_name} vs {next_team.name}"

    season = next_game.season
    season_type = next_game.season_type

    game_thread_text = f"""
|[](/browns2)|
|:-----:|
|**BEHAVE YOURSELVES AND REPORT ANYTHING THAT BREAKS THE RULES.**|
|**FANS OF OTHER TEAMS PLEASE SELECT A FLAIR**|

----

{standings_table}

----

||Game Info|
|:-----:|:-----:|:------:|:------:|
|**Location**|{next_game.venue_name}|
|**When**| Sunday {get_time(next_game.game_time)}|
|**Weather**|{weather_forecast}|
|**Radio**| [Local Radio Link - 92.3 THE FAN](https://player.radio.com/listen/station/923-the-fan), ESPN 850
|**TV Network**| {", ".join(next_game.networks)}
|**TV Coverage**| [Map](https://506sports.com/nfl.php?yr={season}&wk={next_game.week})|
|**Commentary**|??|
|**NFL** |[Game Center](https://www.nfl.com/games/{next_team.name}-at-{team_name}-{season}-{season_type}-{next_game.week})|

----

|Team|Starting QB|
|:-----:|:-----:|
|[{next_team.name}]({next_subreddit})|??|
|[{team_name}]({team_subreddit})|??|

----

||{season} [{next_team.name}]({next_subreddit}) Leaders|{season} [{team_name}]({team_subreddit}) Leaders|
|:-----:|:-----:|:------:|
|**Passing**|{next_pass_lead}|{team_pass_lead}|
|**Rushing**|{next_rush_lead}|{team_rush_lead}|
|**Receiving**|{next_rec_lead}|{team_rec_lead}|
|**Tackles**|{next_tack_lead}|{team_tack_lead}|
|**Interceptions**|{next_int_lead}|{team_int_lead}|
|**Sacks**|{next_sack_lead}|{team_sack_lead}|
    """

    message = f"""
*Body*
```{game_thread_text}```

*Title*
```{title}```
    """
    await send_message(message)


if __name__ == "__main__":
    asyncio.run(generate_game_thread())
