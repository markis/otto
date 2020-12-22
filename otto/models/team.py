import os

from typing import Optional
from typing import Tuple

from otto import ASSETS_DIRECTORY


ABBR_TO_SUBREDDIT = {
    "KC": "/r/kansascitychiefs",
    "OAK": "/r/oaklandraiders",
    "LV": "/r/raiders",
    "DEN": "/r/denverbroncos",
    "LAC": "/r/chargers",
    "IND": "/r/colts",
    "TEN": "/r/tennesseetitans",
    "HOU": "/r/texans",
    "JAX": "/r/jaguars",
    "CIN": "/r/bengals",
    "PIT": "/r/steelers",
    "BAL": "/r/ravens",
    "CLE": "/r/browns",
    "MIA": "/r/miamidolphins",
    "NYJ": "/r/nyjets",
    "BUF": "/r/buffalobills",
    "NE": "/r/patriots",
    "DAL": "/r/cowboys",
    "PHI": "/r/eagles",
    "NYG": "/r/nygiants",
    "WAS": "/r/washingtonnfl",
    "CHI": "/r/chibears",
    "GB": "/r/greenbaypackers",
    "DET": "/r/detroitlions",
    "MIN": "/r/minnesotavikings",
    "ATL": "/r/falcons",
    "NO": "/r/saints",
    "CAR": "/r/panthers",
    "TB": "/r/buccaneers",
    "ARI": "/r/azcardinals",
    "SF": "/r/49ers",
    "LA": "/r/losangelesrams",
    "SEA": "/r/seahawks",
}

ABBR_TO_NAME = {
    "KC": "Chiefs",
    "OAK": "Raiders",
    "LV": "Raiders",
    "DEN": "Broncos",
    "LAC": "Chargers",
    "IND": "Colts",
    "TEN": "Titans",
    "HOU": "Texans",
    "JAX": "Jaguars",
    "CIN": "Bengals",
    "PIT": "Steelers",
    "BAL": "Ravens",
    "CLE": "Browns",
    "MIA": "Dolphins",
    "NYJ": "Jets",
    "BUF": "Bills",
    "NE": "Patriots",
    "DAL": "Cowboys",
    "PHI": "Eagles",
    "NYG": "Giants",
    "WAS": "Washington",
    "CHI": "Bears",
    "GB": "Packers",
    "DET": "Lions",
    "MIN": "Vikings",
    "ATL": "Falcons",
    "NO": "Saints",
    "CAR": "Panthers",
    "TB": "Buccaneers",
    "ARI": "Cardinals",
    "SF": "49ers",
    "LA": "Rams",
    "SEA": "Seahawks",
}

NICKNAME_TO_ABBR = {
    "Chiefs": "KC",
    "Raiders": "LV",
    "Broncos": "DEN",
    "Chargers": "LAC",
    "Colts": "IND",
    "Titans": "TEN",
    "Texans": "HOU",
    "Jaguars": "JAX",
    "Bengals": "CIN",
    "Steelers": "PIT",
    "Ravens": "BAL",
    "Browns": "CLE",
    "Dolphins": "MIA",
    "Jets": "NYJ",
    "Bills": "BUF",
    "Patriots": "NE",
    "Cowboys": "DAL",
    "Eagles": "PHI",
    "Giants": "NYG",
    "Washington": "WAS",
    "Football Team": "WAS",
    "Redskins": "WAS",
    "Bears": "CHI",
    "Packers": "GB",
    "Lions": "DET",
    "Vikings": "MIN",
    "Falcons": "ATL",
    "Saints": "NO",
    "Panthers": "CAR",
    "Buccaneers": "TB",
    "Cardinals": "ARI",
    "49ers": "SF",
    "Rams": "LA",
    "Seahawks": "SEA",
}

ABBR_TO_POSITION = {
    "KC": -225,
    "LV": -360,
    "DEN": -135,
    "LAC": -375,
    "IND": -195,
    "TEN": -450,
    "HOU": -180,
    "JAX": -210,
    "CIN": -90,
    "PIT": -390,
    "BAL": -30,
    "CLE": -105,
    "MIA": -240,
    "NYJ": -345,
    "BUF": -45,
    "NE": -270,
    "DAL": -120,
    "PHI": -500,
    "NYG": -330,
    "WAS": -465,
    "CHI": -75,
    "GB": -165,
    "DET": -150,
    "MIN": -255,
    "ATL": -15,
    "NO": -285,
    "CAR": -60,
    "TB": -435,
    "ARI": 0,
    "SF": -390,
    "LA": -420,
    "SEA": -405,
}

ABBR_TO_LOCATION = {
    "KC": (0, 0),
    "LV": (36.0908159, -115.1831358),
    "DEN": (39.691540, -104.916910),
    "LAC": (0, 0),
    "IND": (39.815140, -86.341640),
    "TEN": (0, 0),
    "HOU": (0, 0),
    "JAX": (0, 0),
    "CIN": (39.096400, -84.515050),
    "PIT": (40.441181, -79.952553),
    "BAL": (39.308530, -76.564780),
    "CLE": (41.506160, -81.699580),
    "MIA": (0, 0),
    "NYJ": (40.814430, -74.078728),
    "BUF": (0, 0),
    "NE": (42.088420, -71.269650),
    "DAL": (0, 0),
    "PHI": (0, 0),
    "NYG": (0, 0),
    "WAS": (0, 0),
    "CHI": (0, 0),
    "GB": (0, 0),
    "DET": (0, 0),
    "MIN": (0, 0),
    "ATL": (0, 0),
    "NO": (0, 0),
    "CAR": (0, 0),
    "TB": (27.977830, -82.503390),
    "ARI": (39.308530, -76.564780),
    "SF": (37.334790, -121.888140),
    "LA": (0, 0),
    "SEA": (0, 0),
}


def get_subreddit(abbr: str) -> str:
    return ABBR_TO_SUBREDDIT[abbr.upper()]


def get_position(abbr: str) -> int:
    return ABBR_TO_POSITION[abbr.upper()]


def get_location(abbr: str) -> Tuple[float, float]:
    return ABBR_TO_LOCATION[abbr.upper()]


def get_abbr(name: str) -> str:
    return NICKNAME_TO_ABBR[name]


def get_name(id: str) -> str:
    return ABBR_TO_NAME[id]


def get_small_icon_path(abbr: str) -> str:
    return os.path.normpath(ASSETS_DIRECTORY + "/small-teams/{}.png".format(abbr))


def get_small_bw_icon_path(abbr: str) -> str:
    return os.path.normpath(ASSETS_DIRECTORY + "/small-bw-teams/{}.png".format(abbr))


class Team:
    abbr: str
    name: str

    def __init__(self, abbr: str, name: str) -> None:
        self.abbr = abbr
        self.name = name
