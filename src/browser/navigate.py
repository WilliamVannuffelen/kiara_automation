import logging

from playwright.async_api import (
    Page,
    Locator,
    TimeoutError as PlaywrightTimeoutError,
    Error as PlaywrightError,
)

from src.browser.locate import get_section_expand_collapse_button
from src.lib.helpers import terminate_script
from src.exceptions.custom_exceptions import BrowserNavigationError

log = logging.getLogger(__name__)

# TODO: Open debug browser and kiara from inside the application
# likely prevents bug where ctx[0] doesn't exist despite page being open
# also more user friendly for the less technically inclined
# can add config.ini setting for alias/path to open debug chrome


# TODO: - add check to see if we're on this page, if we're on any other page
# show popup asking for confirmation to navigate to this page (user might lose data if they've entered shit manually)
async def open_timesheet_page(page: Page) -> None:
    try:
        await page.get_by_role("cell", name="knop ga verder").locator("a").click()
        log.info("Navigated to timesheet page.")
    except PlaywrightTimeoutError as e:
        log.error(
            "Failed to navigate to timesheet page. Ensure you're on the landing page after ACM/IDM authentication."
        )
        log.error(e, exc_info=True)
        terminate_script(1)


async def expand_collapse_section(
    page: Page, search_string: str, collapse: bool
) -> None:
    button_locator = await get_section_expand_collapse_button(
        page=page, search_string=search_string, collapse=collapse
    )
    try:
        await button_locator.click()
        log.info(
            f"{'Collapsed' if collapse else 'Expanded'} section '{search_string}'."
        )
    except PlaywrightTimeoutError as e:
        log.error(f"Failed to collapse or expand section. {e}")


async def navigate_to_page(page: Page, url: str):
    try:
        await page.goto(url)
        log.info(f"Opened page: {url}")
    except (PlaywrightTimeoutError, PlaywrightError) as e:
        log.error(f"Failed to open page: {url}. {e}")
        raise BrowserNavigationError from e


async def click_navigation_button(
    nav_button_locator: Locator, nav_button_name: str, timeout: int = 3000
):
    try:
        await nav_button_locator.click(timeout=timeout)
        log.info(f"Clicked navigation button: '{nav_button_name}'")
    except PlaywrightTimeoutError as e:
        log.error(f"Failed to click navigation button: '{nav_button_name}'")
        raise BrowserNavigationError from e
