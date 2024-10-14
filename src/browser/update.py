import logging

from playwright.async_api import Page

from src.lib.project_helpers import is_empty_value
from src.objects.kiara_work_item import KiaraWorkItem
from src.browser.locate import (
    find_work_item,
    _get_highest_work_item_index,
    is_target_element_present,
)


log = logging.getLogger(__name__)


async def add_work_item_entry(
    page: Page,
    work_item: KiaraWorkItem,
    date_indices: dict,
    task_index: int,
    work_item_index: int,
) -> None:
    # item_date = await _format_date_silly(work_item.date)
    # time_spent = await _format_timespan_silly(work_item.time_spent)

    try:
        column_index = date_indices[work_item.formatted_date]
    except KeyError:
        print(f"Date {work_item.formatted_date} not found in selected week")
        return  # fix proper exc handling etc.
    work_item_locator = page.locator(
        f'input[name="taak[{task_index}].prestatie[{work_item_index}].dagPrestatie[{column_index}].gepresteerdeTijd"]'
    )
    try:
        await work_item_locator.fill(work_item.time_spent)
        await work_item_locator.blur()
        log.info(
            f"Added time to existing work item '{work_item.description}' on '{work_item.date}' - {work_item.time_spent}h"
        )
    except Exception as e:
        log.error(
            f"Failed to add time to existing work item '{work_item.description}' on '{work_item.date}' - {work_item.time_spent}h"
        )
        log.error(e)


async def check_work_item_box(
    page: Page,
    work_item: KiaraWorkItem,
    task_index: int,
    date_indices: dict,
    last_work_item_index: int,
) -> None:
    # need to take last element to avoid broken state due to odd behaviour:
    # A new item bumping the selected copy dummy down an index
    # only changes the index AFTER the second copy action
    # forces a page reload
    # in other words - if it gets bumped down everything breaks
    work_item_locator = page.locator(
        f'input[name="taak[{task_index}].prestatie[{last_work_item_index}].omschrijving"]'
    )
    checkbox_locator = page.locator(
        f'input[name="taak[{task_index}].prestatie[{last_work_item_index}].toBeCopied"]'
    )
    try:
        dupe_description = await work_item_locator.get_attribute("value")
        log.debug(f"Will copy existing work item '{dupe_description}'")
        await checkbox_locator.check()
        log.debug(f"Checked checkbox for work item '{work_item.description}'")
    except Exception as e:
        log.error(f"Failed to check checkbox for work item '{work_item.description}'")
        log.error(e)


async def remember_copied_name(
    page: Page,
    work_item: KiaraWorkItem,
    task_index: int,
    date_indices: dict,
    last_work_item_index: int,
) -> str:
    description_locator = page.locator(
        f'input[name="taak[{task_index}].prestatie[{last_work_item_index}].omschrijving"]'
    )
    copied_work_item_orig_name = await description_locator.get_attribute("value")
    copied_work_item_name = f"Copy {copied_work_item_orig_name}"

    log.debug(f"Target work item name: '{work_item.description}'")
    return copied_work_item_name


async def enter_cell_text(
    page: Page,
    work_item: KiaraWorkItem,
    task_index: int,
    work_item_index: int,
    work_item_column_key: str,
    cell_type_key: str,
) -> None:
    locator_strings = {
        "jira_ref": f"input[name='taak[{task_index}].prestatie[{work_item_index}].incident.lineItem']",
        "app_ref": f"input[name='taak[{task_index}].prestatie[{work_item_index}].toepassing.nummer']",
    }
    has_input = is_empty_value(work_item, work_item_column_key)
    if not has_input:
        return
    locator_str = locator_strings[work_item_column_key]
    locator = page.locator(locator_str)
    item_exists = await is_target_element_present(page, locator, locator_str)
    if item_exists:
        try:
            await locator.fill(getattr(work_item, work_item_column_key))
            log.debug(
                f"Updated {cell_type_key} of work item '{work_item.description}' - '{getattr(work_item,work_item_column_key)}' with value '{getattr(work_item, work_item_column_key)}'"
            )
        except Exception as e:
            log.error(
                f"Failed to update {cell_type_key} of work item '{work_item.description}' - '{getattr(work_item, work_item_column_key)}'"
            )
            log.error(e)
    else:
        pass


async def add_new_work_item(
    page: Page, work_item: KiaraWorkItem, task_index: int, date_indices: dict
):
    # grab last index
    last_work_item_index = await _get_highest_work_item_index(page, task_index)

    await check_work_item_box(
        page, work_item, task_index, date_indices, last_work_item_index
    )
    copied_work_item_name = await remember_copied_name(
        page, work_item, task_index, date_indices, last_work_item_index
    )

    try:
        await page.locator('img[alt="knop voeg nieuwe activiteit toe"]').click()
        await page.wait_for_url(
            "https://kiara.vlaanderen.be/Kiara/secure/tijdsregistratie/detailtijdsregistratie.do"
        )
        log.debug(f"Added new dummy work item '{copied_work_item_name}'")
    except Exception as e:
        log.error(f"Failed to add new dummy work item '{copied_work_item_name}'")
        log.error(e)

    work_item_index = await find_work_item(
        page,
        KiaraWorkItem(description=copied_work_item_name),
        task_index,
        is_copy=True,
        target_description=work_item.description,
    )

    # update description
    description_locator = page.locator(
        f'input[name="taak[{task_index}].prestatie[{work_item_index}].omschrijving"]'
    )
    try:
        await description_locator.fill(work_item.description)
        log.debug(f"Updated description of new work item '{work_item.description}'")
    except Exception as e:
        log.error(
            f"Failed to update description of new work item '{work_item.description}'"
        )
        log.error(e)

    await enter_cell_text(
        page, work_item, task_index, work_item_index, "jira_ref", "jira_ref"
    )
    await enter_cell_text(
        page, work_item, task_index, work_item_index, "app_ref", "app_ref"
    )

    if work_item.app_ref:
        line_item_locator = page.locator(
            f'input[name="taak[{task_index}].prestatie[{work_item_index}].toepassing.nummer"]'
        )
        await line_item_locator.fill(work_item.app_ref)

    # add time
    await add_work_item_entry(
        page, work_item, date_indices, task_index, work_item_index
    )
