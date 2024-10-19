import logging

import asyncio
from playwright.async_api import async_playwright

from src.browser.core import init_playwright
from src.browser.navigate import (
    open_timesheet_page,
    expand_collapse_section,
    save_timesheet_provisionally,
)
from src.browser.process_work_items import process_project
from src.browser.authentication import run_authentication_flow

from src.objects.kiara_project import KiaraProject
from src.exceptions.custom_exceptions import (
    DebugBrowserConnectionError,
    BrowserNavigationError,
)

log = logging.getLogger(__name__)


async def run_browser_automation(
    input_config_values: dict, projects: list[KiaraProject]
):
    launch_type = input_config_values["launch_type"]
    phone_number = input_config_values["phone_number"]
    preferred_project = input_config_values["preferred_project"]
    auto_submit = input_config_values["auto_submit"]

    async with async_playwright() as p:
        try:
            browser, page = await init_playwright(playwright=p, launch_type=launch_type)
        except DebugBrowserConnectionError as e:
            raise e

        try:
            if launch_type == "internal":
                await run_authentication_flow(page=page, phone_number=phone_number)
        except Exception as e:
            raise e

        try:
            await open_timesheet_page(page=page)
        except BrowserNavigationError as e:
            log.warning("Attempting to continue.")

        for project in projects:
            if not project.is_general_task:
                await process_project(page, project)

        await expand_collapse_section(
            page=page, search_string="Project-gerelateerde Taken", collapse=True
        )
        await expand_collapse_section(
            page=page, search_string="Algemene Taken", collapse=False
        )

        for project in projects:
            if project.is_general_task:
                await process_project(page, project)

        await expand_collapse_section(
            page=page, search_string="Algemene Taken", collapse=True
        )
        await expand_collapse_section(
            page=page, search_string="Project-gerelateerde Taken", collapse=False
        )

        await expand_collapse_section(
            page=page,
            search_string=preferred_project,
            collapse=False,
        )

        if auto_submit == "true":
            await save_timesheet_provisionally(page=page)

        if launch_type == "internal":
            await asyncio.sleep(3600)
        else:
            log.info("Browser was launched externally. Disconnecting.")

        await browser.close()
