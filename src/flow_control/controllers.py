import logging
from typing import cast

from playwright.async_api import Page, async_playwright

from src.browser.core import init_playwright
from src.browser.locate import (
    get_date_column_indices,
    get_task_index,
    get_task_locator,
    test_work_item_exists,
    get_expand_general_tasks_locator,
)
from src.browser.navigate import collapse_project, expand_project, expand_general_tasks
from src.browser.update import add_new_work_item, add_work_item_entry
from src.exceptions.custom_exceptions import (
    InputDataProcessingError,
    BrowserNavigationError,
)
from src.input.prep_data import (
    convert_to_work_item,
    group_work_items,
    read_input_file,
    truncate_dataframe,
    validate_df_columns,
)
from src.objects.kiara_project import KiaraProject
from src.objects.kiara_work_item import KiaraWorkItem

log = logging.getLogger(__name__)


def process_input_data(file_name: str, sheet_name: str) -> list[KiaraProject]:
    try:
        df = read_input_file(file_name, sheet_name)
        df = truncate_dataframe(df)
        validate_df_columns(df)
        work_items = convert_to_work_item(df)
        projects = group_work_items(work_items)
        return projects
    except Exception as e:
        raise InputDataProcessingError(
            f"Failed to process input data: '{type(e)}'"
        ) from e


async def run_browser_automation(projects: list[KiaraProject]):
    async with async_playwright() as p:
        browser, page = await init_playwright(p)

        # TODO: Add validation to see if we're on landing page, skip if not
        # await open_timesheet_page(page, ctx)

        for project in projects:
            await process_project(page, project)

        try:
            general_tasks_locator = await get_expand_general_tasks_locator(page)
            await expand_general_tasks(page, general_tasks_locator)
        except BrowserNavigationError as e:
            log.error(f"Failed to expand general tasks: '{e}'")

        await browser.close()


async def process_work_item(
    page: Page, work_item: KiaraWorkItem, date_indices: dict, task_index: int
):
    log.info(
        f"Processing work item '{work_item.description}' for date '{work_item.date}'"
    )

    test_work_item_result = await test_work_item_exists(
        page, work_item, date_indices, task_index
    )

    if test_work_item_result.exists:
        log.debug(f"Work item '{work_item.description}' already exists.")
        await add_work_item_entry(
            page,
            work_item,
            date_indices,
            task_index,
            cast(int, test_work_item_result.index),
        )
    else:
        log.debug(f"Work item '{work_item.description}' does not exist yet. Creating.")
        await add_new_work_item(page, work_item, task_index, date_indices)


async def process_project(page: Page, project: KiaraProject):
    project_name = project.name
    work_items = project.items
    log.info(f"Processing project '{project_name}'.")

    task_locator = await get_task_locator(page, project_name)
    task_index = await get_task_index(task_locator)

    await expand_project(page, project_name)

    date_indices = await get_date_column_indices(page)

    for work_item in work_items:
        await process_work_item(page, work_item, date_indices, task_index)

    await collapse_project(page, project_name)
