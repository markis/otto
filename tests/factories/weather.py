import factory
from factory.fuzzy import FuzzyInteger, FuzzyText

from otto.models.weather import Weather


class WeatherFactory(factory.Factory):  # type: ignore[misc]
    """Factory for Game model."""

    class Meta:
        """Meta class for GameFactory."""

        model = Weather

    forecast = FuzzyText(length=10)
    temperature = FuzzyInteger(0, 100)
    wind_speed = FuzzyText(length=10)
    wind_direction = FuzzyText(length=10)
