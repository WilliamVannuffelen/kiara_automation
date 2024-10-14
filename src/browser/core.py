from playwright.async_api import Playwright, Browser, Page
import logging
from src.exceptions.custom_exceptions import DebugBrowserConnectionError

log = logging.getLogger(__name__)

async def init_playwright(playwright: Playwright) -> tuple[Browser,Page]:
    try:
        browser = await playwright.chromium.connect_over_cdp("http://localhost:9222")
        log.debug("Connected to browser.")
    except Exception as e:
        raise DebugBrowserConnectionError("Failed to connect to browser.") from e

    ctx = browser.contexts[0]
    page = ctx.pages[0]
    return browser, page
