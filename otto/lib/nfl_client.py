import operator
import re
from typing import Any, Final, Self, cast

import requests

from otto import logger as root_logger
from otto.constants import DEFAULT_TIMEOUT, TEAM_NAME
from otto.models.game import Game
from otto.models.record import Record

API_URL: Final = "https://api.nfl.com"
logger = root_logger.getChild("lib.nfl_client")


class NFLClient:
    """Client for interacting with the NFL API."""

    _token: str | None = None

    def get_scores(self: Self, team: str = TEAM_NAME) -> list[Game]:
        """Get the scores for a given team. Defaults to the current team."""
        data = self._get_api_data(
            """
              /v1/games?s={{
                "$query":{{
                  "week.season": 2021,
                  "$or":[
                    {{"homeTeam.abbr":"{}"}},
                    {{"visitorTeam.abbr":"{}"}}
                  ]
                }}
              }}&fs={{
                id,
                gameTime,
                week{{
                  season,
                  seasonType,
                  week
                }},
                homeTeam{{
                  id,
                  abbr,
                  nickName
                }},
                visitorTeam{{
                  id,
                  abbr,
                  nickName
                }},
                homeTeamScore{{
                  pointsTotal
                }},
                visitorTeamScore{{
                  pointsTotal
                }},
                gameStatus{{
                  phase
                }},
                venue{{
                  name,
                  location
                }},
                networkChannels
              }}
            """.format(team, team),
        )

        return [Game.from_nfl_dict(game_data) for game_data in data["data"]]

    def get_stat_leader(
        self: Self,
        stat: str = "passing.yards",
        team: str = TEAM_NAME,
        season: str = "2021",
        season_type: str = "REG",
    ) -> str:
        """Get the stat leader for a given stat, team, season, and season type."""
        stat_query = stat.replace(".", "{") + "}"
        data = self._get_api_data(
            """
            /v1/playerTeamStats?s={{
              "$query":{{
                "season":{},
                "seasonType":"{}",
                "team.abbr":"{}"
              }},"$sort":{{
                "{}":1
              }},
              "$take":10,
              "$skip":0
            }}&fs={{
              person{{
                firstName,
                lastName,
              }},
              {},
            }}
            """.format(season, season_type, team, stat, stat_query),
        )
        result = ""
        if data["data"]:
            players = data["data"]
            first_person = data["data"][0]
            top_stat_value = self._get_stat_value(stat, first_person)
            names = []
            for player in players:
                stat_value = self._get_stat_value(stat, player)
                if stat_value and top_stat_value <= stat_value:
                    names.append(player["person"]["firstName"] + " " + player["person"]["lastName"])
            result = ", ".join(names)

        return result

    def _get_stat_value(self: Self, stat: str, player: dict[str, Any]) -> int:
        """Get the value of a stat for a given player."""
        # Stat example: "passing.yards", "defensive.interceptions"
        # person example: { "firstName": "Baker", "lastName": "Mayfield"}.
        stat_value = 0
        stat_pieces = stat.split(".")
        next_entry = player
        for stat_piece in stat_pieces:
            next_entry = next_entry.get(stat_piece, {})
        if next_entry and ((isinstance(next_entry, str) and next_entry.isdigit()) or (isinstance(next_entry, int))):
            stat_value = int(next_entry)
        return stat_value

    def get_game(self: Self, game_id: str) -> dict[str, Any]:
        """Get the game data for a given game ID."""
        data = self._get_api_data(
            """
              /v3/shield/?variables=null&query=query{
                viewer{
                  game(
                    id:"%s"
                  ){
                    id,
                    networkChannels,
                    gameTime,
                    awayTeam{
                      id,
                      abbreviation,
                      fullName,
                      nickName,
                      cityStateRegion,
                      franchise{
                        id,
                        currentLogo{
                          url
                        }
                      }
                    }
                    homeTeam{
                      id,
                      abbreviation,
                      fullName,
                      nickName,
                      cityStateRegion,
                      franchise{
                        id,
                        currentLogo{
                          url
                        }
                      }
                    }
                    week{
                      seasonValue,
                      id,
                      seasonType,
                      weekValue,
                      weekType
                    }
                    radioLinks,
                    ticketUrl,
                    venue{
                      fullName,
                      city,
                      state
                    }
                    gameDetailId
                  }
                }
              }
            """
            % (game_id),
        )
        return cast(dict[str, Any], data["data"]["viewer"]["game"])

    def get_game_details(self: Self, game_id: str) -> dict[str, Any]:
        """Get the game details for a given game ID."""
        return self._get_api_data(
            """
                /v3/shield/?variables=null&query=query{
                    viewer{
                    gameDetail(id:"%s"){
                        id,
                        attendance,
                        distance,
                        down,
                        gameClock,
                        goalToGo,
                        homePointsOvertime,
                        homePointsTotal,
                        homePointsQ1,
                        homePointsQ2,
                        homePointsQ3,
                        homePointsQ4,
                        homeTeam{
                        abbreviation,
                        nickName
                        },
                        homeTimeoutsUsed,
                        homeTimeoutsRemaining,
                        period,
                        phase,
                        playReview,
                        possessionTeam{
                        abbreviation,
                        nickName
                        },
                        redzone,
                        scoringSummaries{
                        playId,
                        playDescription,
                        patPlayId,
                        homeScore,
                        visitorScore
                        },
                        stadium,
                        startTime,
                        visitorPointsOvertime,
                        visitorPointsOvertimeTotal,
                        visitorPointsQ1,
                        visitorPointsQ2,
                        visitorPointsQ3,
                        visitorPointsQ4,
                        visitorPointsTotal,
                        visitorTeam{
                        abbreviation,
                        nickName
                        },
                        visitorTimeoutsUsed,
                        visitorTimeoutsRemaining,
                        homePointsOvertimeTotal,
                        visitorPointsOvertimeTotal,
                        possessionTeam{
                        nickName
                        },
                        weather{
                        currentFahrenheit,
                        location,
                        longDescription,
                        shortDescription,
                        currentRealFeelFahrenheit,
                        }
                        yardLine,
                        yardsToGo,
                        drives{
                        quarterStart,
                        endTransition,
                        endYardLine,
                        endedWithScore,
                        firstDowns,
                        gameClockEnd,
                        gameClockStart,
                        howEndedDescription,
                        howStartedDescription,
                        inside20,
                        orderSequence,
                        playCount,
                        playIdEnded,
                        playIdStarted,
                        playSeqEnded,
                        playSeqStarted,
                        possessionTeam{
                            abbreviation,
                            nickName,
                            franchise{
                            currentLogo{
                                url,
                            },
                            },
                        },
                        quarterEnd,
                        realStartTime,
                        startTransition,
                        startYardLine,
                        timeOfPossession,
                        yards,
                        yardsPenalized
                        },
                        plays{
                        clockTime,
                        down,
                        driveNetYards,
                        drivePlayCount,
                        driveSequenceNumber,
                        driveTimeOfPossession,
                        endClockTime,
                        endYardLine,
                        firstDown,
                        goalToGo,
                        nextPlayIsGoalToGo,
                        nextPlayType,
                        orderSequence,
                        penaltyOnPlay,
                        playClock,
                        playDeleted,
                        playDescription,
                        playDescriptionWithJerseyNumbers,
                        playId,
                        playReviewStatus,
                        isBigPlay,
                        playType,
                        playStats{
                            statId,
                            yards,
                            team{
                            id,
                            abbreviation
                            },
                            playerName,
                            gsisPlayer{ id }
                        }
                        possessionTeam{
                            abbreviation,
                            nickName,
                            franchise{
                            currentLogo{
                                url,
                            }
                            }
                        }
                        prePlayByPlay,
                        quarter,
                        scoringPlay,
                        scoringPlayType,
                        scoringTeam{
                            id,
                            abbreviation,
                            nickName
                        },
                        shortDescription,
                        specialTeamsPlay,
                        stPlayType,
                        timeOfDay,
                        yardLine,
                        yards,
                        yardsToGo,
                        latestPlay
                        }
                    }
                    }
                }
            """
            % (game_id),
        )

    def get_standings(
        self: Self,
        year: str = "2021",
        teams: list[str] | None = None,
        division: str = "AFC_NORTH",
    ) -> list[Record]:
        """Get the current standings for a given year and division.

        If no division is given, the entire league is returned.
        """
        data = self._get_api_data(
            """
            /v3/shield/?variables=null&query=query{
                viewer{
                    standings(
                    first:1,
                    orderBy:week__weekValue,
                    orderByDirection:DESC,
                    week_seasonValue:%s,
                    week_seasonType:REG,
                    ){
                        edges{
                            cursor
                            node{
                                id
                                teamRecords{
                                    conference
                                    division
                                    fullName
                                    nickName
                                    overallWin
                                    overallLoss
                                    overallTie
                                    overallPct
                                    overallPtsFor
                                    overallPtsAgainst
                                    homeWin
                                    homeLoss
                                    homeTie
                                    homePct
                                    roadWin
                                    roadLoss
                                    roadTie
                                    roadPct
                                    divisionWin
                                    divisionLoss
                                    divisionTie
                                    divisionPct
                                    divisionRank
                                    conferenceWin
                                    conferenceLoss
                                    conferenceTie
                                    conferencePct
                                    conferenceRank
                                    overallStreak
                                    clinchDivision
                                    clinchDivisionAndHomefield
                                    clinchPlayoff
                                    clinchWc
                                    eliminatedFromPostseason
                                }
                            }
                        }
                    }
                }
            }
            """
            % (year),
        )
        edges = data["data"]["viewer"]["standings"]["edges"]
        team_records = edges[0]["node"]["teamRecords"] if edges else []
        records = [Record(team_record) for team_record in team_records]
        if teams:
            records = [record for record in records if record.abbr in teams]
        elif division:
            records = [record for record in records if record.division == division]
            records.sort(key=operator.attrgetter("division_rank"))
        return records

    def _get_api_data(self: Self, url: str) -> dict[str, Any]:
        """Get data from the NFL API."""
        url = API_URL + re.sub(r"[\n\s]+", " ", url).strip()
        res = requests.get(
            url=url,
            headers={"Authorization": "Bearer " + self._get_client_token()},
            timeout=DEFAULT_TIMEOUT,
        )
        try:
            return cast(dict[str, Any], res.json())
        except:
            logger.exception("Error getting data from NFL API, url: %s, result: %s", url, res.text)
            raise

    def _get_client_token(self: Self) -> str:
        if self._token:
            return self._token

        url = API_URL + "/v1/reroute"

        res = requests.post(
            url=url,
            data={"grant_type": "client_credentials"},
            headers={"X-Domain-Id": "100"},
            timeout=DEFAULT_TIMEOUT,
        )

        self._token = res.json()["access_token"]
        assert isinstance(self._token, str)
        return self._token
