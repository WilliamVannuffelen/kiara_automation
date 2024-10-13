import logging
import asyncio
import contextvars
import datetime
import re
import uuid

import pandas as pd
from playwright.async_api import async_playwright, Playwright, Locator, Page

from src.lib.helpers import init_logging
from src.browser.core import init_playwright
from src.browser.locate import (
    get_task_locator,
    get_task_index,
    get_date_column_indices,
    find_work_item,
    test_work_item_exists,
)
from src.browser.navigate import open_timesheet_page, expand_project, collapse_project
from src.lib.project_helpers import _format_date_silly, _format_timespan_silly
from src.browser.update import add_work_item_entry, add_new_work_item
from src.config.input import get_args #, read_input_file, add_project_column, split_projects, add_dummy_jira_ref, input_validate_app_ref
from src.input.prep_data import prep_data
from src.models.kiara_project import KiaraProject


def main():
    file_name, sheet_name = get_args()
    projects = prep_data(file_name, sheet_name)
    
    asyncio.run(async_main(projects))


async def async_main(projects: list[KiaraProject]):
    async with async_playwright() as p:
        browser = await init_playwright(p)
        ctx = browser.contexts[0]
        page = ctx.pages[0]

        # start from home page after ACM/IDM logon:
        # navigate to timesheet page and expand relevant project

        # TODO: Add validation to see if we're on landing page, skip if not
        # await open_timesheet_page(page, ctx)

        for project in projects:
            project_name = project.name
            work_items = project.items
            log.info(f"Processing project '{project_name}'.")
            # grab task locator
            task_locator = await get_task_locator(
                page, project_name
            )
            # grab task index
            task_index = await get_task_index(task_locator)

            # open project
            await expand_project(
                page, project_name
            )

            date_indices = await get_date_column_indices(page)

            for work_item in work_items:
                print(work_item)
                log.info(
                    f"Processing work item '{work_item.description}' for date '{work_item.date}'"
                )
                log.debug(f"{work_item}.")
                work_item_exists, work_item_index = await test_work_item_exists(
                    page, work_item, date_indices, task_index
                )

                if work_item_exists:
                    await add_work_item_entry(
                        page, work_item, date_indices, task_index, work_item_index
                    )
                else:
                    await add_new_work_item(page, work_item, task_index, date_indices)

            await collapse_project(
              page, project_name
            )
        await browser.close()


if __name__ == "__main__":
    init_logging(name="main", log_level="debug")
    try:
        log = logging.getLogger("main")
        log.info("Script started.")
    except Exception as e:
        print(f"Failed to initiate logger.")
        print(e)
        helpers._terminate_script(1)

    main()
