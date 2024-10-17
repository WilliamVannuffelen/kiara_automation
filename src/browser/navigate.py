import logging

from playwright.async_api import Page, TimeoutError as PlaywrightTimeoutError

from src.browser.locate import get_section_expand_collapse_button
from src.lib.helpers import terminate_script

log = logging.getLogger(__name__)


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
