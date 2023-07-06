import logging
from pathlib import Path
from typing import Any, Final

from playwright.async_api import async_playwright

from otto import TWITTER_AUTH_COOKIE

COOKIES: Final[list[Any]] = [
    {
        "name": "auth_token",
        "value": TWITTER_AUTH_COOKIE,
        "domain": ".twitter.com",
        "path": "/",
        "httpOnly": True,
        "secure": True,
    },
]

logger: Final = logging.getLogger(__name__)


async def screenshot_article(url: str, path: str | Path) -> bool:
    try:
        async with async_playwright() as p:
            browser = await p.firefox.launch()
            context = await browser.new_context(color_scheme="dark")
            await context.add_cookies(COOKIES)
            page = await context.new_page()
            await page.goto(url)
            element = await page.wait_for_selector("article")
            assert element
            await element.screenshot(path=path)
            await browser.close()
            return True
    except Exception as e:
        logger.error("Error screenshotting article", exc_info=e)
        return False
