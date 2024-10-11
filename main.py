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


def get_work_items(path: str, date: str):
    df = pd.read_excel(io=path, sheet_name=date, usecols="A:E")
    return df.to_dict("records")


def main():
    work_items = get_work_items("~/wvl/devel/tempo/t_upload.xlsx", "2024-09-30")
    asyncio.run(async_main(work_items))


async def async_main(work_items: list):
    async with async_playwright() as p:
        browser = await init_playwright(p)
        ctx = browser.contexts[0]
        page = ctx.pages[0]

        # start from home page after ACM/IDM logon:
        # navigate to timesheet page and expand relevant project

        # TODO: Add validation to see if we're on landing page, skip if not
        # await open_timesheet_page(page, ctx)

        # # grab task locator
        # task_locator = await get_task_locator(
        #     page, "CS0126444 - Wonen Cloudzone - dedicated operationeel projectteam"
        # )
        # # grab task index
        # task_index = await get_task_index(task_locator)

        # # open project
        # await expand_project(
        #     page, "CS0126444 - Wonen Cloudzone - dedicated operationeel projectteam"
        # )

        # date_indices = await get_date_column_indices(page)

        # for work_item in work_items:
        #     log.info(
        #         f"Processing work item '{work_item["Description"]}' for date '{work_item["Date"]}'"
        #     )
        #     log.debug(f"{work_item.items()}.")
        #     work_item_exists, work_item_index = await test_work_item_exists(
        #         page, work_item, date_indices, task_index
        #     )

        #     if work_item_exists:
        #         await add_work_item_entry(
        #             page, work_item, date_indices, task_index, work_item_index
        #         )
        #     else:
        #         await add_new_work_item(page, work_item, task_index, date_indices)

        await collapse_project(
            page, "CS0126444 - Wonen Cloudzone - dedicated operationeel projectteam"
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
