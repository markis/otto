import inspect

from typing import Any
from unittest.mock import Mock


def record_data(name: str, data: Any) -> None:
    import json

    f = open(f"./tests/data/{name}.json", "w")
    json.dump(data, f)
    f.close()


def generate() -> None:
    from otto.lib.nfl_client import NFLClient

    nflclient = NFLClient()
    _original_api_data = nflclient._get_api_data

    def data_logger(url: str) -> Any:
        curframe = inspect.currentframe()
        calframe = inspect.getouterframes(curframe, 2)
        caller = calframe[1][3]
        data = _original_api_data(url)

        record_data(caller, data)
        return data

    nflclient._get_api_data = data_logger  # type: ignore

    # NFL Client calls to get data
    nflclient.get_scores()
    nflclient.get_standings()
    nflclient.get_stat_leader()
    nflclient.get_game("10012019-0808-5525-9974-889293498212")
    nflclient.get_game_details("10160000-0578-4035-d1b9-6f446209f715")


if __name__ == "__main__":
    generate()
