import logging
import re
from typing import cast

from playwright.async_api import Locator, Page

from src.objects.kiara_work_item import KiaraWorkItem, TestWorkItemResult

log = logging.getLogger(__name__)


async def is_target_element_present(
    page: Page, locator: Locator, locator_string: str
) -> bool:
    try:
        await locator.element_handle()
        log.debug(f"Element found for '{locator_string}'")
        return True
    except Exception as e:
        log.debug(f"Element not found for '{locator_string}'")
        log.debug(e)
        return False


async def get_task_locator(page: Page, search_string: str) -> Locator:
    cell_locator = page.get_by_role("cell", name=search_string, exact=True)
    return cell_locator


async def get_task_index(locator: Locator) -> int:
    inner_html = await locator.inner_html()

    pattern = re.compile(r"taak\[(\d+)\]")
    task_index = pattern.search(inner_html)

    return task_index.group(1)


async def get_date_column(page: Page, date: str) -> Locator:
    date_column = page.get_by_role("columnheader", name=date, exact=True)
    return date_column


async def get_date_column_indices(page: Page) -> dict[str, int]:
    date_indices: dict[str, int] = {}
    days = ["Ma", "Di", "Wo", "Do", "Vr", "Za", "Zo"]
    for i in range(0, 7):
        headers_locator = page.locator(
            "table:nth-of-type(4) tr:nth-of-type(3) th"
        ).filter(has_text=re.compile(f"^{days[i]}"))
        inner_text = await headers_locator.inner_text()
        date_elems = inner_text.split("\n")[1].split("/")
        date = f"{date_elems[1]}-{date_elems[0]}"
        date_indices[date] = i
    return date_indices


async def _get_highest_work_item_index(page: Page, task_index: int) -> int:
    work_item_selector = (
        f'input[name^="taak[{task_index}].prestatie["][name$="].omschrijving"]'
    )

    work_items = await page.query_selector_all(work_item_selector)

    last_item_name = await work_items[-1].get_attribute("name")
    log.debug(f"Last item name: {last_item_name}")

    match = re.search(r"prestatie\[(\d+)\]", last_item_name)
    last_item_index = match.group(1)
    log.debug(f"Matches: {match.groups()}")
    log.debug(f"Last item index: {last_item_index}")

    return last_item_index


async def test_work_item_exists(
    page: Page, work_item: KiaraWorkItem, date_indices: dict, task_index: int
) -> TestWorkItemResult:

    try:
        work_item_index = await find_work_item(page, work_item, task_index)
        log.debug(f"Work item index: {work_item_index}")
    except Exception as e:
        log.error(f"Error finding work item: {e}")
        return TestWorkItemResult(False, None)

    return TestWorkItemResult(work_item_index is not None, work_item_index)


async def find_work_item(
    page: Page,
    work_item: KiaraWorkItem,
    task_index: int,
    is_copy: bool = False,
    target_description: str = "",
) -> int | None:
    # lower because uppercase first char breaks kiara sorting :)
    description = (
        work_item.description.lower()
        if work_item.description[0:4] != "Copy"
        else work_item.description
    )

    last_item_index = await _get_highest_work_item_index(page, task_index)
    log.debug(f"Last item index in current project table '{last_item_index}'")

    item_index = None
    for i in range(0, int(last_item_index) + 1):
        work_item_locator = page.locator(
            f'input[name="taak[{task_index}].prestatie[{i}].omschrijving"]'
        )

        val = cast(str, await work_item_locator.get_attribute("value"))
        if val.lower() == description.lower():
            if is_copy:
                log.info(
                    f"Found existing dummy work item '{description}' for target '{target_description}' at index '{i}'"
                )
            item_index = i
            break
        else:
            continue

    if item_index is None:
        log.info(f"No existing work item found for description '{description}'")
        return None
    else:
        log.info(f"Found existing work item '{description}' at index '{item_index}'")
        return item_index
