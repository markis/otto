class Weather:
    forecast: str
    temperature: int
    wind_speed: str
    wind_direction: str

    def __init__(self, data: dict[str, str]):
        self.forecast = data["shortForecast"]
        self.temperature = int(data["temperature"])
        self.wind_direction = data["windDirection"]
        self.wind_speed = data["windSpeed"]
