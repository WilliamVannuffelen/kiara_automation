import logging

from playwright.async_api import Page

from src.browser.locate import find_work_item
from src.lib.project_helpers import _format_date_silly, _format_timespan_silly

log = logging.getLogger(__name__)


async def add_work_item_entry(
    page: Page,
    work_item: dict,
    date_indices: dict,
    task_index: int,
    work_item_index: int,
) -> None:
    item_date = await _format_date_silly(work_item["Date"])
    time_spent = await _format_timespan_silly(work_item["TimeSpent"])

    try:
        column_index = date_indices[item_date]
    except KeyError:
        print(f"Date {item_date} not found in selected week")
        return  # fix proper exc handling etc.
    work_item_locator = page.locator(
        f'input[name="taak[{task_index}].prestatie[{work_item_index}].dagPrestatie[{column_index}].gepresteerdeTijd"]'
    )
    try:
        await work_item_locator.fill(time_spent)
        await work_item_locator.blur()
        log.info(
            f"Added time to existing work item '{work_item["Description"]}' on '{work_item["Date"]}' - {time_spent}h"
        )
    except Exception as e:
        log.error(
            f"Failed to add time to existing work item '{work_item['Description']}' on '{work_item['Date']}' - {time_spent}h"
        )
        log.error(e)


async def check_work_item_box(
    page: Page, work_item: dict, task_index: int, date_indices: dict
) -> None:
    # find & check button of elem number 0 to copy to a new task
    # take index 1 because new item will become 0
    checkbox_locator = page.locator(
        f'input[name="taak[{task_index}].prestatie[1].toBeCopied"]'
    )
    try:
        await checkbox_locator.check()
        log.debug(f"Checked checkbox for work item '{work_item['Description']}'")
    except Exception as e:
        log.error(
            f"Failed to check checkbox for work item '{work_item['Description']}'"
        )
        log.error(e)


async def remember_copied_name(
    page: Page, work_item: dict, task_index: int, date_indices: dict
) -> str:
    description_locator = page.locator(
        f'input[name="taak[{task_index}].prestatie[1].omschrijving"]'
    )
    copied_work_item_orig_name = await description_locator.get_attribute("value")
    copied_work_item_name = f"Copy {copied_work_item_orig_name}"

    log.debug(f"Target work item name: '{work_item['Description']}'")
    return copied_work_item_name


async def add_new_work_item(
    page: Page, work_item: dict, task_index: int, date_indices: dict
):
    await check_work_item_box(page, work_item, task_index, date_indices)
    copied_work_item_name = await remember_copied_name(
        page, work_item, task_index, date_indices
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
        {"Description": copied_work_item_name},
        task_index,
        is_copy=True,
        target_description=work_item["Description"],
    )

    # update description
    description_locator = page.locator(
        f'input[name="taak[{task_index}].prestatie[{work_item_index}].omschrijving"]'
    )
    try:
        await description_locator.fill(work_item["Description"])
        log.debug(f"Updated description of new work item '{work_item['Description']}'")
    except Exception as e:
        log.error(
            f"Failed to update description of new work item '{work_item['Description']}'"
        )
        log.error(e)

    # update jira ref
    line_item_locator = page.locator(
        f'input[name="taak[{task_index}].prestatie[{work_item_index}].incident.lineItem"]'
    )
    await line_item_locator.fill(work_item["JiraRef"])

    # add time
    await add_work_item_entry(
        page, work_item, date_indices, task_index, work_item_index
    )
