from playwright.async_api import Page
from typing import Optional, cast
import logging
from src.objects.kiara_project import KiaraProject
from src.objects.kiara_work_item import KiaraWorkItem, TestWorkItemResult
from src.browser.locate import get_task_locator, get_task_index, get_date_column_indices, test_work_item_exists
from src.browser.navigate import expand_project, collapse_project
from src.browser.update import add_work_item_entry, add_new_work_item

log = logging.getLogger(__name__)

async def process_work_item(page: Page, work_item: KiaraWorkItem, date_indices: dict, task_index: int):
    log.info(f"Processing work item '{work_item.description}' for date '{work_item.date}'")
    
    test_work_item_result = await test_work_item_exists(
        page, work_item, date_indices, task_index
    )

    if test_work_item_result.exists:
        log.debug(f"Work item '{work_item.description}' already exists.")
        await add_work_item_entry(
            page, work_item, date_indices, task_index, cast(int, test_work_item_result.index)
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

    await expand_project(
        page, project_name
    )

    date_indices = await get_date_column_indices(page)

    for work_item in work_items:
        await process_work_item(page, work_item, date_indices, task_index)

    await collapse_project(
        page, project_name
    )