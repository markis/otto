import os

import requests


SENDBIRD_API_TOKEN = os.environ.get("SENDBIRD_API_TOKEN")


def send_message(message: str, channel_url: str, from_id: str = "t2_3ip6y4pw") -> None:
    url = "https://api-reddit.sendbird.com/v3/bots/" + from_id + "/send"

    requests.post(
        url=url,
        json={"message": message, "channel_url": channel_url},
        headers={"Api-Token": SENDBIRD_API_TOKEN},
    )
