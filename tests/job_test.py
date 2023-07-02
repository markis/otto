from unittest.mock import MagicMock, patch

from tests.mock import STRUCTURED_STYLES, get_mock_reddit, get_mock_request_get

# from tests.mock import NFL_API_GAME_RESPONSE
# from tests.mock import NFL_API_STANDINGS_RESPONSE


# @fixture(autouse=True)
# def block_requests(monkeypatch: Any) -> None:
#     """ Ensure accidents don't happen """
#     monkeypatch.delattr("urllib.request.urlretrieve")


@patch("otto.get_reddit", new_callable=get_mock_reddit)
@patch("requests.get", new_callable=get_mock_request_get)
@patch("requests.post")
@patch("requests.head")
def test_jobs(
    requests_head: MagicMock,
    requests_post: MagicMock,
    requests_get: MagicMock,
    get_reddit: MagicMock,
) -> None:
    requests_post.side_effect = [MagicMock(json=MagicMock(return_value={"access_token": "123"}))]
    # requests_get.side_effect = [
    #     MagicMock(json=MagicMock(return_value=NFL_API_GAME_RESPONSE)),
    #     MagicMock(json=MagicMock(return_value=NFL_API_STANDINGS_RESPONSE)),
    # ]
    requests_head.return_value = MagicMock(headers={"age": 0})

    from otto.job import run_jobs
    from otto.lib.update_sidebar_score import spacer

    reddit = get_reddit()
    reddit.get = MagicMock(return_value=STRUCTURED_STYLES)
    config = MagicMock()
    run_jobs(config=config, reddit=reddit, timer=MagicMock(start=MagicMock()))

    widgets = reddit.subreddit().widgets.sidebar
    widgets[0].mod.update.assert_called_once_with(
        text="\n"
        + "\n".join(
            [
                f"{spacer}**Date**{spacer}||**Opponent**|{spacer}**Time**{spacer}",
                ":--:|:--:|:--|:--:",
                "|08/08|vs|[](/r/washingtonnfl) WAS|W 30-10|",
                "|08/17|@ |[](/r/colts) IND|W 21-18|",
                "|08/23|@ |[](/r/buccaneers) TB|L 12-13|",
                "|08/29|vs|[](/r/detroitlions) DET|W 20-16|",
            ]
        )
    )
    widgets[1].mod.update.assert_called_once_with(
        text="\n"
        + "\n".join(
            [
                f"{spacer}**Date**{spacer}||**Opponent**|{spacer}**Time**{spacer}",
                ":--:|:--:|:--|:--:",
                "|09/08|vs|**[Titans](/r/tennesseetitans)**|L 13-43|",
                "|09/16|@ |**[Jets](/r/nyjets)**|W 23-3|",
                "|09/22|vs|**[Rams](/r/losangelesrams)**|L 13-20|",
                "|09/29|@ |**[Ravens](/r/ravens)**|W 40-25|",
                "|10/07|@ |**[49ers](/r/49ers)**|L 3-31|",
                "|10/13|vs|**[Seahawks](/r/seahawks)**|L 28-32|",
                "|BYE|||",
                "|10/27|@ |**[Patriots](/r/patriots)**|L 13-27|",
                "|11/03|@ |**[Broncos](/r/denverbroncos)**|L 19-24|",
                "|11/10|vs|**[Bills](/r/buffalobills)**|W 19-16|",
                "|11/14|vs|**[Steelers](/r/steelers)**|W 21-7|",
                "|11/24|vs|**[Dolphins](/r/miamidolphins)**|W 41-24|",
                "|12/01|@ |**[Steelers](/r/steelers)**|L 13-20|",
                "|12/08|vs|**[Bengals](/r/bengals)**|W 27-19|",
                "|12/15|@ |**[Cardinals](/r/azcardinals)**|L 24-38|",
                "|12/22|vs|**[Ravens](/r/ravens)**|L 15-31|",
                "|12/29|@ |**[Bengals](/r/bengals)**|1:00|",
            ]
        )
    )
    widgets[2].mod.update.assert_called_once_with(
        text="\n"
        + "\n".join(
            [
                "||**W-L**|**Home**|**Away**|**Div**|**Streak**|",
                "|:---:|:--:|:--:|:--:|:--:|:--:|",
                "|[](/r/ravens)(BAL)|13-2|6-1|7-1|4-1|11W|",
                "|[](/r/steelers)(PIT)|8-7|5-3|3-4|3-2|2L|",
                "|[](/r/browns)(CLE)|6-9|4-4|2-5|3-2|2L|",
                "|[](/r/bengals)(CIN)|1-14|1-6|0-8|0-5|3L|",
            ]
        )
    )
