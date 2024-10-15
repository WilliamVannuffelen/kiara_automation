import logging

from playwright.async_api import Page

from src.browser.locate import get_task_index
from src.lib.helpers import _terminate_script

log = logging.getLogger(__name__)


async def open_timesheet_page(page: Page, ctx) -> None:
    try:
        await page.get_by_role("cell", name="knop ga verder").locator("a").click()
        log.info("Navigated to timesheet page.")
    except Exception as e:
        log.error(
            "Failed to navigate to timesheet page. Ensure you're on the landing page after ACM/IDM authentication."
        )
        log.error(e)
        _terminate_script(1)


async def expand_project(page: Page, search_string: str) -> None:
    cell_locator = page.get_by_role("cell", name=search_string, exact=True)
    await get_task_index(cell_locator)

    row_locator = cell_locator.locator("..")
    try:
        await row_locator.get_by_role("cell", name="Expand").get_by_role("img").click()
        log.info(f"Expanded project '{search_string}'.")
    except Exception as e:
        log.error(f"Failed to expand project '{search_string}'.")
        log.error(e)
        _terminate_script(1)


async def collapse_project(page: Page, search_string: str) -> None:
    cell_locator = page.get_by_role("cell", name=search_string, exact=True)
    await get_task_index(cell_locator)

    row_locator = cell_locator.locator("..")
    try:
        await row_locator.get_by_role("cell", name="Collapse").get_by_role(
            "img"
        ).click()
        log.info(f"Collapsed project '{search_string}'.")
    except Exception as e:
        log.error(f"Failed to collapse project '{search_string}'.")
        log.error(e)
