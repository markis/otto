import factory
from factory.fuzzy import FuzzyChoice

from otto.models.team import ABBR_TO_NAME, Team


class TeamFactory(factory.Factory):  # type: ignore[misc]
    """Factory for Team model."""

    class Meta:
        """Meta class for TeamFactory."""

        model = Team

    abbr = FuzzyChoice(ABBR_TO_NAME.keys())
    name = FuzzyChoice(ABBR_TO_NAME.values())
