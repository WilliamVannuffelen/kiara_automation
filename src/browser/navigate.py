from playwright.async_api import Page, Locator

import src.browser.locate as locate


async def open_timesheet_page(page: Page, ctx) -> None:
    await page.get_by_role("cell", name="knop ga verder").locator("a").click()


async def expand_project(page: Page, search_string: str) -> None:
    cell_locator = page.get_by_role("cell", name=search_string, exact=True)
    await locate.get_task_index(cell_locator)

    row_locator = cell_locator.locator("..")
    await row_locator.get_by_role("cell", name="Expand").get_by_role("img").click()
