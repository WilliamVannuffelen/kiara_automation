import logging

from playwright.async_api import Page, Locator

from src.browser.locate import get_task_index, get_section_expand_collapse_button
from src.lib.helpers import _terminate_script

log = logging.getLogger(__name__)


async def open_timesheet_page(page: Page) -> None:
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
    row_locator = cell_locator.locator("..")
    try:
        await row_locator.get_by_role("cell", name="Expand").get_by_role("img").click()
        log.info(f"Expanded project '{search_string}'.")
    except Exception as e:
        log.error(f"Failed to expand project '{search_string}'.")
        log.error(e)
        _terminate_script(1)


async def expand_general_tasks(locator: Locator) -> None:
    try:
        await locator.get_by_role("img").click()
        log.info("Expanded general tasks.")
    except Exception as e:
        log.error("Failed to expand general tasks.")
        log.error(e)
        _terminate_script(1)


async def collapse_project_section(page: Page) -> None:
    try:
        row_locator = page.get_by_role(
            "cell", name="Project-gerelateerde Taken", exact=True
        ).locator("..")
        collapse_button_locator = row_locator.get_by_role(
            "cell", name="Collapse"
        ).get_by_role("img")
        await collapse_button_locator.click()
        log.info("Collapsed project section.")
    except Exception as e:
        log.error(f"Failed to collapse project section. {e}")


async def collapse_major_section(page: Page, search_string: str) -> None:
    try:
        row_locator = page.get_by_role("cell", name=search_string, exact=True).locator(
            ".."
        )
        collapse_button_locator = row_locator.get_by_role(
            "cell", name="Collapse"
        ).get_by_role("img")
        await collapse_button_locator.click()
        log.info("Collapsed major section.")
    except Exception as e:
        log.error(f"Failed to collapse major section. {e}")


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
    except Exception as e:
        log.error(f"Failed to collapse or expand section. {e}")


async def collapse_project(page: Page, search_string: str) -> None:
    cell_locator = page.get_by_role("cell", name=search_string, exact=True).locator(
        ".."
    )
    await get_task_index(cell_locator)

    row_locator = cell_locator.locator("..")
    try:
        await row_locator.get_by_role("cell", name="Collapse").get_by_role("img").nth(
            1
        ).click()
        log.info(f"Collapsed project '{search_string}'.")
    except Exception as e:
        log.error(f"Failed to collapse project '{search_string}'.")
        log.error(e)
