import logging
import asyncio

from playwright.async_api import async_playwright

from src.lib.helpers import init_logging, _terminate_script
from src.browser.core import init_playwright
from src.config.input import get_args
from src.input.prep_data import prep_data
from src.objects.kiara_project import KiaraProject
from src.flow_control.controllers import process_project


def main():
    file_name, sheet_name = get_args()
    projects = prep_data(file_name, sheet_name)
    asyncio.run(async_main(projects))


async def async_main(projects: list[KiaraProject]):
    async with async_playwright() as p:
        browser, page = await init_playwright(p)

        # TODO: Add validation to see if we're on landing page, skip if not
        # await open_timesheet_page(page, ctx)

        for project in projects:
            await process_project(page, project)

        await browser.close()


if __name__ == "__main__":
    init_logging(name="main", log_level="debug")
    try:
        log = logging.getLogger("main")
        log.info("Script started.")
    except Exception as e:
        print(f"Failed to initiate logger. {e}")
        _terminate_script(1)

    main()
