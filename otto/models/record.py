from typing import Self

from otto.models.team import get_abbr


class Record:
    """Represents a team's record."""

    abbr: str

    win: int
    loss: int
    tie: int
    streak: str

    conference: str
    conference_rank: int
    conference_win: int
    conference_loss: int
    conference_tie: int

    division: str
    division_rank: int
    division_win: int
    division_loss: int
    division_tie: int

    home_win: int
    home_loss: int
    home_tie: int

    road_win: int
    road_loss: int
    road_tie: int

    def __init__(self: Self, data: dict[str, str]) -> None:
        """Initialize a Record object."""
        self.abbr = get_abbr(data["nickName"])

        self.win = int(data["overallWin"])
        self.loss = int(data["overallLoss"])
        self.tie = int(data["overallTie"])
        self.streak = data["overallStreak"]

        self.conference = data["conference"]
        self.conference_rank = int(data["conferenceRank"])
        self.conference_win = int(data["conferenceWin"])
        self.conference_loss = int(data["conferenceLoss"])
        self.conference_tie = int(data["conferenceTie"])

        self.division = data["division"]
        self.division_rank = int(data["divisionRank"])
        self.division_win = int(data["divisionWin"])
        self.division_loss = int(data["divisionLoss"])
        self.division_tie = int(data["divisionTie"])

        self.home_win = int(data["homeWin"])
        self.home_loss = int(data["homeLoss"])
        self.home_tie = int(data["homeTie"])

        self.road_win = int(data["roadWin"])
        self.road_loss = int(data["roadLoss"])
        self.road_tie = int(data["roadTie"])
