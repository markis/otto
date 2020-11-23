from datetime import datetime
from typing import Any
from typing import Optional

from requests import get

from otto.models.weather import Weather
from otto.utils import convert_tzstring
from otto.utils import get_now


class WeatherClient:
    def get_weather(
        self, lat: float, long: float, date: datetime = get_now()
    ) -> Optional[Weather]:
        url = "https://api.weather.gov/points/{lat},{long}".format(lat=lat, long=long)
        res = get(url)

        links = res.json()
        if links and "properties" in links:
            res = get(links["properties"].get("forecast"))
            weather = res.json()

            periods = weather["properties"]["periods"]
            for period in periods:
                forecast_start = convert_tzstring(period["startTime"])
                forecast_end = convert_tzstring(period["endTime"])

                if forecast_start <= date and forecast_end >= date:
                    return Weather(period)
        return None
