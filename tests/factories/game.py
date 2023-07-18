from datetime import UTC, datetime

import factory
import hypothesis.strategies as st
from factory.fuzzy import FuzzyChoice, FuzzyDateTime, FuzzyInteger

from otto.models.game import Game
from tests.factories.team import TeamFactory

SEASON = 2023


class GameFactory(factory.Factory):  # type: ignore[misc]
    """Factory for Game model."""

    class Meta:
        """Meta class for GameFactory."""

        model = Game

    game_id = factory.Faker("uuid4")
    game_detail_id = factory.Faker("uuid4")
    game_time = FuzzyDateTime(datetime(SEASON, 9, 1, tzinfo=UTC), datetime(SEASON + 1, 1, 31, tzinfo=UTC))
    season = str(SEASON)
    season_type = FuzzyChoice(["REG", "PRE", "POST"])
    week = factory.Faker("pyint", min_value=1, max_value=17)
    at_home = st.booleans()
    opponent = factory.SubFactory(TeamFactory)
    home_score = FuzzyInteger(0, 50)
    visitor_score = FuzzyInteger(0, 50)
    game_phase = FuzzyChoice(["PREGAME", "IN_PROGRESS", "FINAL"])
    venue_name = factory.Faker("company")
    venue_city = factory.Faker("city")
    venue_state = factory.Faker("state_abbr")
    networks = factory.List([factory.Faker("word") for _ in range(3)])
    data = factory.Dict({"key": factory.Faker("word")})
