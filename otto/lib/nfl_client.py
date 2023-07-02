import operator
import re
from typing import Any, Final

import requests

from otto import TEAM_NAME
from otto.models.game import Game
from otto.models.record import Record

API_URL: Final = "https://api.nfl.com"


class NFLClient:
    _token: str | None = None

    def get_scores(self, team: str = TEAM_NAME) -> list[Game]:
        data = self._get_api_data(
            """
              /v1/games?s={
                "$query":{
                  "week.season": 2021,
                  "$or":[
                    {"homeTeam.abbr":"%s"},
                    {"visitorTeam.abbr":"%s"}
                  ]
                }
              }&fs={
                id,
                gameTime,
                week{
                  season,
                  seasonType,
                  week
                },
                homeTeam{
                  id,
                  abbr,
                  nickName
                },
                visitorTeam{
                  id,
                  abbr,
                  nickName
                },
                homeTeamScore{
                  pointsTotal
                },
                visitorTeamScore{
                  pointsTotal
                },
                gameStatus{
                  phase
                },
                venue{
                  name,
                  location
                },
                networkChannels
              }
            """  # noqa: UP031
            % (team, team)
        )

        return [Game.from_nfl_dict(game_data) for game_data in data["data"]]

    def get_stat_leader(
        self,
        stat: str = "passing.yards",
        team: str = TEAM_NAME,
        season: str = "2021",
        season_type: str = "REG",
    ) -> str:
        stat_query = stat.replace(".", "{") + "}"
        data = self._get_api_data(
            """
            /v1/playerTeamStats?s={
              "$query":{
                "season":%s,
                "seasonType":"%s",
                "team.abbr":"%s"
              },"$sort":{
                "%s":1
              },
              "$take":10,
              "$skip":0
            }&fs={
              person{
                firstName,
                lastName,
              },
              %s,
            }
          """  # noqa: UP031
            % (season, season_type, team, stat, stat_query)
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

    def _get_stat_value(self, stat: str, player: dict[str, Any]) -> int:
        """
        stat example: "passing.yards", "defensive.interceptions"
        person example: { "firstName": "Baker", "lastName": "Mayfield"}
        """
        stat_value = 0
        stat_pieces = stat.split(".")
        if stat_pieces and len(stat_pieces) >= 2:
            first_piece = stat_pieces[0]
            second_piece = stat_pieces[1]
            stat_value = int(player.get(first_piece, {}).get(second_piece, 0))
        return stat_value

    # def get_venues(self):
    #     url = """
    #       /v3/shield/?variables=null&query=query{
    #         viewer{
    #           venue(id:"%s") {

    #           }
    #         }
    #       }
    #     """
    #     url = API_URL + re.sub(r"[\n\s]+", " ", url).strip()
    #     res = requests.get(
    #         url=url, headers={"Authorization": "Bearer " + self._get_client_token()}
    #     )
    #     return res.status_code

    def get_game(self, game_id: str) -> Any:
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
            """  # noqa: UP031
            % (game_id)
        )
        return data["data"]["viewer"]["game"]

    def get_game_details(self, id: str) -> Any:
        data = self._get_api_data(
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
       """  # noqa: UP031
            % (id)
        )
        return data

    def get_standings(
        self,
        year: str = "2021",
        teams: list[str] | None = None,
        division: str = "AFC_NORTH",
    ) -> list[Record]:
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
            """  # noqa: UP031
            % (year)
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

    def _get_api_data(self, url: str) -> Any:
        url = API_URL + re.sub(r"[\n\s]+", " ", url).strip()
        res = requests.get(url=url, headers={"Authorization": "Bearer " + self._get_client_token()})
        try:
            return res.json()
        except:
            print(url)
            print(res.text)
            raise

    def _get_client_token(self, refresh: bool = False) -> str:
        if not refresh and self._token:
            return self._token

        url = API_URL + "/v1/reroute"

        res = requests.post(
            url=url,
            data={"grant_type": "client_credentials"},
            headers={"X-Domain-Id": "100"},
        )

        self._token = res.json()["access_token"]
        assert isinstance(self._token, str)
        return self._token
