from playwright.async_api import Playwright


async def init_playwright(playwright: Playwright) -> Playwright.chromium:
    browser = await playwright.chromium.connect_over_cdp("http://localhost:9222")
    return browser
