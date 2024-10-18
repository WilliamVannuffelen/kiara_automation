import re
import logging
from typing import cast

import asyncio
from playwright.async_api import Page, async_playwright

from src.browser.core import init_playwright
from src.browser.locate import (
    get_date_column_indices,
    get_task_index,
    get_task_locator,
    test_work_item_exists,
    get_authentication_method_button,
    get_phone_number_input_box,
    get_target_element,
)
from src.browser.navigate import (
    navigate_to_page,
    open_timesheet_page,
    expand_collapse_section,
    click_navigation_button,
)
from src.browser.update import (
    add_new_work_item,
    add_work_item_entry,
    enter_cell_text_generic,
)
from src.exceptions.custom_exceptions import (
    InputDataProcessingError,
    BrowserNavigationError,
    TargetElementNotFoundError,
    BrowserFillCellError,
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


async def run_browser_automation(
    input_config_values: dict, projects: list[KiaraProject]
):
    launch_type = input_config_values["launch_type"]
    phone_number = input_config_values["phone_number"]
    preferred_project = input_config_values["preferred_project"]

    async with async_playwright() as p:
        browser, page = await init_playwright(playwright=p, launch_type=launch_type)

        try:
            if launch_type == "internal":
                await run_authentication_flow(page=page, phone_number=phone_number)
        except Exception as e:
            raise e

        # TODO: Add validation to see if we're on landing page, skip if not
        await open_timesheet_page(page=page)

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
        if launch_type == "internal":
            await save_timesheet_provisionally(page=page)
        else:
            log.info("Browser launched externally. Disconnecting.")

        await browser.close()


async def run_authentication_flow(page: Page, phone_number: str) -> None:
    """
    Only supports itsme.
    """
    log.info("Running authentication flow.")

    await navigate_to_page(page, "https://kiara.vlaanderen.be")
    await select_authentication_method(page, "itsme")
    await auth_with_mfa(page, phone_number)


async def select_authentication_method(page: Page, method: str):
    log.info(f"Selecting authentication method: '{method}'")
    try:
        auth_method_locator = await get_authentication_method_button(page, method)
        await click_navigation_button(
            nav_button_locator=auth_method_locator,
            nav_button_name=method,
            timeout=15000,
        )
    except Exception as e:
        raise BrowserNavigationError from e


async def auth_with_mfa(page: Page, phone_number: str) -> None:
    try:
        phone_number_input_locator = await get_phone_number_input_box(page)
        log.info(f"Authenticating with MFA using phone number: '{phone_number}'")
    except TargetElementNotFoundError as e:
        raise BrowserNavigationError from e
    try:
        await enter_cell_text_generic(
            phone_number_input_locator, phone_number, "phone number"
        )
    except BrowserFillCellError as e:
        raise e
    try:
        trigger_mfa_button_locator = await get_target_element(
            page.locator("button", has_text="Versturen"), "trigger MFA button"
        )
        log.info("Triggered MFA prompt.")
    except TargetElementNotFoundError as e:
        raise BrowserNavigationError from e
    try:
        await click_navigation_button(
            nav_button_locator=trigger_mfa_button_locator,
            nav_button_name="Trigger MFA",
            timeout=15000,
        )
    except Exception as e:
        raise BrowserNavigationError from e

    await page.wait_for_url(re.compile(r"^https://kiara\.vlaanderen\.be"))


async def save_timesheet_provisionally(page: Page) -> None:
    log.info("Saving timesheet provisionally.")
    try:
        save_button_locator = page.get_by_role(
            "cell", name="knop bewaar voorlopig"
        ).locator("a")
        await save_button_locator.element_handle()
    except TargetElementNotFoundError as e:
        raise BrowserNavigationError from e
    try:
        await click_navigation_button(
            nav_button_locator=save_button_locator,
            nav_button_name="Save timesheet provisionally",
            timeout=15000,
        )
    except Exception as e:
        raise BrowserNavigationError from e


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
            page=page,
            work_item=work_item,
            date_indices=date_indices,
            task_index=task_index,
            work_item_index=cast(int, test_work_item_result.index),
        )
    else:
        log.debug(f"Work item '{work_item.description}' does not exist yet. Creating.")
        await add_new_work_item(
            page=page,
            work_item=work_item,
            task_index=task_index,
            date_indices=date_indices,
        )


async def process_project(page: Page, project: KiaraProject):
    project_name = project.name
    work_items = project.items
    log.info(f"Processing project '{project_name}'.")

    task_locator = await get_task_locator(
        page=page, search_string=project_name, is_general_task=project.is_general_task
    )
    task_index = await get_task_index(locator=task_locator)

    await expand_collapse_section(page=page, search_string=project_name, collapse=False)

    date_indices = await get_date_column_indices(page)

    for work_item in work_items:
        await process_work_item(page, work_item, date_indices, task_index)

    await expand_collapse_section(page=page, search_string=project_name, collapse=True)
