import logging

from playwright.async_api import Browser, Page, Playwright

from src.exceptions.custom_exceptions import DebugBrowserConnectionError

log = logging.getLogger(__name__)


async def init_playwright(playwright: Playwright) -> tuple[Browser, Page]:
    try:
        browser = await playwright.chromium.connect_over_cdp("http://localhost:9222")
        log.debug("Connected to browser.")
    except Exception as e:
        raise DebugBrowserConnectionError("Failed to connect to browser.") from e

    # TODO: Sometimes ctx is completely empty despite the debug browser having the target page open
    # not sure how to solve this inside code since it requires a new tab to be opened in the debug browser
    # might just throw a descriptive error and let the user know to open a new tab in the debug browser
    ctx = browser.contexts[0]
    ctx.set_default_timeout(3000)
    page = ctx.pages[0]
    return browser, page
