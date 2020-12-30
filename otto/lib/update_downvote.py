from datetime import datetime
from typing import List

import praw

from otto.config import Config
from otto.models.game import Game
from otto.models.game import get_last_game
from otto.models.game import get_next_game
from otto.models.team import get_position
from otto.models.team import get_small_bw_icon_path
from otto.models.team import get_small_icon_path
from otto.utils import get_url_age
from otto.utils.css import find_all_rules_by_classes
from otto.utils.css import get_identity
from otto.utils.css import get_token_value_by_ident
from otto.utils.css import parse_stylesheet
from otto.utils.css import serialize_stylesheet


def update_downvote(
    config: Config, reddit: praw.Reddit, sr_name: str, games: List[Game]
) -> None:
    sr = reddit.subreddit(sr_name)
    next_game = get_next_game(games, config.downvotes_delay)
    last_game = get_last_game(games, config.downvotes_delay)
    assert next_game
    next_team = next_game.opponent
    assert next_team
    next_abbr = next_team.abbr
    assert last_game
    last_game_datetime = last_game.game_time

    # Update old reddit
    update_old_downvote(sr, next_abbr)

    # Update new reddit
    update_new_downvote(reddit, sr, next_abbr, last_game_datetime)


def update_new_downvote(
    reddit: praw.Reddit,
    sr: praw.models.Subreddit,
    next_abbr: str,
    last_game_datetime: datetime,
) -> None:
    assert sr, "`sr` wasn't specified"
    assert next_abbr, "`next_abbr` wasn't specified"

    data = reddit.get(praw.const.API_PATH["structured_styles"].format(subreddit=sr))

    current_downvote_icon_inactive_age = get_url_age(
        data["data"]["style"]["postDownvoteIconInactive"]
    )

    if (
        current_downvote_icon_inactive_age < last_game_datetime
        or current_downvote_icon_inactive_age < last_game_datetime
    ):
        active_image_path = get_small_icon_path(next_abbr)
        inactive_image_path = get_small_bw_icon_path(next_abbr)

        active_down_url = sr.stylesheet._upload_style_asset(
            active_image_path, "postDownvoteIconActive"
        )
        inactive_down_url = sr.stylesheet._upload_style_asset(
            inactive_image_path, "postDownvoteIconInactive"
        )
        sr.stylesheet._update_structured_styles(
            {
                "postVoteIcons": "custom",
                "postDownvoteIconActive": active_down_url,
                "postDownvoteIconInactive": inactive_down_url,
            }
        )


def update_old_downvote(sr: praw.models.Subreddit, team: str) -> None:
    assert sr, "`sr` wasn't specified"
    assert team, "`team` wasn't specified"

    # Update old Reddit
    DOWNVOTE_UNVOTED_TOKEN = "%%teamsmallfade%%"
    DOWNVOTE_UNVOTED = ".arrow.down"
    DOWNVOTE_VOTED_TOKEN = "%%teamsmall%%"
    DOWNVOTE_VOTED = ".arrow.downmod"

    sr_stylesheet = sr.stylesheet
    styles = sr_stylesheet.__call__()
    css = styles.stylesheet

    parsed = parse_stylesheet(css)
    rules = find_all_rules_by_classes({DOWNVOTE_UNVOTED, DOWNVOTE_VOTED}, parsed)

    for rule in rules:
        identity = get_identity(rule)
        if identity == DOWNVOTE_UNVOTED:
            background_position = get_token_value_by_ident(rule, "background-position")
            background_position[0].representation = str(0)
            background_position[1].representation = str(get_position(team))

            background_image = get_token_value_by_ident(rule, "background-image")
            background_image[0].value = DOWNVOTE_UNVOTED_TOKEN

        elif identity == DOWNVOTE_VOTED:
            background_position = get_token_value_by_ident(rule, "background-position")
            background_position[0].representation = str(0)
            background_position[1].representation = str(get_position(team))

            background_image = get_token_value_by_ident(rule, "background-image")
            background_image[0].value = DOWNVOTE_VOTED_TOKEN

    updated_css = serialize_stylesheet(parsed)
    sr_stylesheet.update(updated_css)
