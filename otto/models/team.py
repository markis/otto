import os

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
    "LAC": -240,
    "IND": -195,
    "TEN": -450,
    "HOU": -180,
    "JAX": -210,
    "CIN": -90,
    "PIT": -390,
    "BAL": -30,
    "CLE": -105,
    "MIA": -270,
    "NYJ": -345,
    "BUF": -45,
    "NE": -300,
    "DAL": -120,
    "PHI": -375,
    "NYG": -330,
    "WAS": -465,
    "CHI": -75,
    "GB": -165,
    "DET": -150,
    "MIN": -285,
    "ATL": -15,
    "NO": -315,
    "CAR": -60,
    "TB": -435,
    "ARI": 0,
    "SF": -420,
    "LA": -255,
    "SEA": -405,
}

ABBR_TO_LOCATION = {
    "KC": (39.048847, -94.481577),
    "LV": (36.0908159, -115.1831358),
    "DEN": (39.691540, -104.916910),
    "LAC": (33.9533893, -118.340906),
    "IND": (39.815140, -86.341640),
    "TEN": (36.1664833, -86.7734838),
    "HOU": (29.6847265, -95.4129014),
    "JAX": (30.3239582, -81.6394468),
    "CIN": (39.096400, -84.515050),
    "PIT": (40.441181, -79.952553),
    "BAL": (39.308530, -76.564780),
    "CLE": (41.506160, -81.699580),
    "MIA": (25.9579713, -80.2410544),
    "NYJ": (40.8135104, -74.076651),
    "BUF": (42.7737585, -78.7891663),
    "NE": (42.088420, -71.269650),
    "DAL": (32.7472889, -97.0966879),
    "PHI": (39.901196, -75.1689085),
    "NYG": (40.8135104, -74.076651),
    "WAS": (38.9076475, -76.8667394),
    "CHI": (41.8623536, -87.6178414),
    "GB": (44.5013444, -88.0644023),
    "DET": (42.3400103, -83.047797),
    "MIN": (44.9736499, -93.2596885),
    "ATL": (33.7554535, -84.4030452),
    "NO": (29.9510656, -90.0834382),
    "CAR": (35.2258152, -80.8550405),
    "TB": (27.977830, -82.503390),
    "ARI": (39.308530, -76.564780),
    "SF": (37.334790, -121.888140),
    "LA": (33.9533893, -118.340906),
    "SEA": (47.594913, -122.3335843),
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
