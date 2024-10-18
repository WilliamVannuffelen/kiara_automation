import logging

from playwright.async_api import Browser, Page, Playwright

from src.exceptions.custom_exceptions import DebugBrowserConnectionError

log = logging.getLogger(__name__)


async def init_playwright(
    playwright: Playwright, launch_type: str
) -> tuple[Browser, Page]:
    if launch_type == "external":
        log.debug("Launch type is external. Connecting to existing browser.")
        try:
            browser = await playwright.chromium.connect_over_cdp(
                "http://localhost:9222"
            )
            log.debug("Connected to browser.")

        except Exception as e:
            raise DebugBrowserConnectionError("Failed to connect to browser.") from e
        ctx = browser.contexts[0]
        ctx.set_default_timeout(3000)
        page = ctx.pages[0]
    else:
        log.debug("Launch type is internal. Launching new browser.")
        try:
            browser = await playwright.chromium.launch(headless=False)
            log.debug("Launched browser.")
        except Exception as e:
            raise DebugBrowserConnectionError("Failed to launch browser.") from e
        ctx = await browser.new_context()
        ctx.set_default_timeout(3000)
        page = await ctx.new_page()

    # TODO: Sometimes ctx is completely empty despite the debug browser having the target page open
    # not sure how to solve this inside code since it requires a new tab to be opened in the debug browser
    # might just throw a descriptive error and let the user know to open a new tab in the debug browser

    return browser, page
