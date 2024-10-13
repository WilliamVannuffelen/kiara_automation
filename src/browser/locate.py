import logging
import re
from playwright.async_api import Locator, Page

log = logging.getLogger(__name__)


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


async def get_date_column_indices(page: Page) -> dict:
    date_indices = {}
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


async def _get_highest_work_item_index(page: Page, task_index: int):
    work_item_selector = (
        f'input[name^="taak[{task_index}].prestatie["][name$="].omschrijving"]'
    )
    work_items = await page.query_selector_all(work_item_selector)

    last_item_name = await work_items[-1].get_attribute("name")

    match = re.search(r"prestatie\[(\d+)\]", last_item_name)
    last_item_index = match.group(1)

    return last_item_index


async def test_work_item_exists(
    page: Page, work_item: dict, date_indices: dict, task_index: int
) -> tuple[bool, int | bool, None]:

    work_item_index = await find_work_item(page, work_item, task_index)
    if work_item_index is None:
        return False, None
    else:
        return True, work_item_index


async def find_work_item(
    page: Page,
    work_item: dict,
    task_index: int,
    is_copy: bool = False,
    target_description: str = None,
) -> int | None:
    # lower because uppercase first char breaks kiara sorting :)
    description = (
        work_item["Description"].lower()
        if work_item["Description"][0:4] != "Copy"
        else work_item["Description"]
    )

    last_item_index = await _get_highest_work_item_index(page, task_index)
    log.debug(f"Last item index in current project table '{last_item_index}'")

    item_index = None
    for i in range(0, int(last_item_index)):
        work_item_locator = page.locator(
            f'input[name="taak[{task_index}].prestatie[{i}].omschrijving"]'
        )
        val = await work_item_locator.get_attribute("value")
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
        return item_index
