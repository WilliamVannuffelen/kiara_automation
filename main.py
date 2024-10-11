import asyncio
from playwright.async_api import async_playwright, Playwright, Locator, Page
import re
import datetime
import pandas as pd
import lib.helpers as helpers
import contextvars
import uuid


def get_work_items(path: str, date: str):
    df = pd.read_excel(io=path, sheet_name=date, usecols="A:E")
    return df.to_dict("records")


async def run(playwright: Playwright) -> Playwright.chromium:
    browser = await playwright.chromium.connect_over_cdp("http://localhost:9222")
    return browser


async def open_timesheet_page(page: Page, ctx) -> None:
    await page.get_by_role("cell", name="knop ga verder").locator("a").click()


async def get_task_locator(page: Page, search_string: str) -> Locator:
    cell_locator = page.get_by_role("cell", name=search_string, exact=True)
    return cell_locator


async def get_task_index(locator: Locator) -> int:
    inner_html = await locator.inner_html()

    pattern = re.compile(r"taak\[(\d+)\]")
    task_index = pattern.search(inner_html)

    return task_index.group(1)


async def expand_project(page: Page, search_string: str) -> None:
    cell_locator = page.get_by_role("cell", name=search_string, exact=True)
    await get_task_index(cell_locator)

    row_locator = cell_locator.locator("..")
    await row_locator.get_by_role("cell", name="Expand").get_by_role("img").click()


async def _format_date_silly(date: str):
    date_parts = date.split("-")
    date_parts = [re.sub(r"^0", "", part) for part in date_parts]
    return f"{date_parts[1]}-{date_parts[2]}"


async def _format_timespan_silly(time_spent: float):
    """valid input: integers + 0.25 | 0.5 | 0.75"""
    hours = int(time_spent)
    minutes = int((time_spent % 1) * 60)
    return f"{hours}.{minutes}"


async def get_date_column(page: Page, date: str):
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


async def find_work_item(page: Page, work_item: dict, task_index: int, is_copy: bool = False, target_description: str = None) -> int | None:
    # lower because uppercase first char breaks kiara sorting :)
    description = (
        work_item["Description"].lower()
        if work_item["Description"][0:4] != "Copy"
        else work_item["Description"]
    )

    last_item_index = await _get_highest_work_item_index(page, task_index)
    log.debug(f"Last item index in table '{last_item_index}'")

    item_index = None
    for i in range(0, int(last_item_index)):
        work_item_locator = page.locator(
            f'input[name="taak[{task_index}].prestatie[{i}].omschrijving"]'
        )
        val = await work_item_locator.get_attribute("value")
        if val.lower() == description.lower():
            if is_copy:
                log.info(f"Found existing work item '{target_description}' at index '{i}'")
            item_index = i
            break
        else:
            continue

    if item_index is None:
        log.info(f"No existing work item found for description '{description}'")
        return None
    else:
        return item_index


async def test_work_item_exists(
    page: Page, work_item: dict, date_indices: dict, task_index: int
) -> tuple[bool, int | bool, None]:

    work_item_index = await find_work_item(page, work_item, task_index)
    if work_item_index is None:
        return False, None
    else:
        return True, work_item_index


async def add_work_item_entry(
    page: Page,
    work_item: dict,
    date_indices: dict,
    task_index: int,
    work_item_index: int,
) -> None:
    item_date = await _format_date_silly(work_item["Date"])
    try:
        column_index = date_indices[item_date]
    except KeyError:
        print(f"Date {item_date} not found in selected week")
        return  # fix proper exc handling etc.
    work_item_locator = page.locator(
        f'input[name="taak[{task_index}].prestatie[{work_item_index}].dagPrestatie[{column_index}].gepresteerdeTijd"]'
    )

    time_spent = await _format_timespan_silly(work_item["TimeSpent"])
    try:
        await work_item_locator.fill(time_spent)
        await work_item_locator.blur()
        log.info(f"Added time to existing work item '{work_item["Description"]}' on '{work_item["Date"]}' - {time_spent}h")
    except Exception as e:
        log.error(f"Failed to add time to existing work item '{work_item['Description']}' on '{work_item['Date']}' - {time_spent}h")
        log.error(e)
  



async def add_new_work_item(
    page: Page, work_item: dict, task_index: int, date_indices: dict
):
    # find & check button of elem number 0 to copy to a new task
    # take index 1 because new item will become 0
    checkbox_locator = page.locator(
        f'input[name="taak[{task_index}].prestatie[1].toBeCopied"]'
    )
    await checkbox_locator.check()

    # store name to find new task later
    description_locator = page.locator(
        f'input[name="taak[{task_index}].prestatie[1].omschrijving"]'
    )
    copied_work_item_orig_name = await description_locator.get_attribute("value")
    copied_work_item_name = f"Copy {copied_work_item_orig_name}"
    log.debug(f"Target work item name: '{work_item['Description']}'")

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
        page, {"Description": copied_work_item_name}, task_index, is_copy=True, target_description=work_item["Description"]
    )

    # update description
    description_locator = page.locator(
        f'input[name="taak[{task_index}].prestatie[{work_item_index}].omschrijving"]'
    )
    try:
        await description_locator.fill(work_item["Description"])
        log.debug(f"Updated description of new work item '{work_item['Description']}'")
    except Exception as e:
        log.error(f"Failed to update description of new work item '{work_item['Description']}'")
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


def main():
    work_items = get_work_items("~/wvl/devel/tempo/t_upload.xlsx", "2024-09-30")
    asyncio.run(async_main(work_items))


async def async_main(work_items: list):
    async with async_playwright() as p:
        browser = await run(p)
        ctx = browser.contexts[0]
        page = ctx.pages[0]

        # start from home page after ACM/IDM logon:
        # navigate to timesheet page and expand relevant project
        #await open_timesheet_page(page, ctx)

        # grab task locator
        task_locator = await get_task_locator(
            page, "CS0126444 - Wonen Cloudzone - dedicated operationeel projectteam"
        )
        # grab task index
        task_index = await get_task_index(task_locator)

        # open project
        #await expand_project(
        #    page, "CS0126444 - Wonen Cloudzone - dedicated operationeel projectteam"
        #)

        # grab column indices for each date in the selected week
        date_indices = await get_date_column_indices(page)

        for work_item in work_items:
            log.info(f"Processing work item '{work_item["Description"]}' for date '{work_item["Date"]}'")
            log.debug(f"{work_item.items()}.")
            # check if item exists
            # if do: add time
            # if dont': make new
            work_item_exists, work_item_index = await test_work_item_exists(
                page, work_item, date_indices, task_index
            )

            if work_item_exists:
                # add time to existing item
                await add_work_item_entry(
                    page, work_item, date_indices, task_index, work_item_index
                )
            else:
                # make work item
                await add_new_work_item(page, work_item, task_index, date_indices)

        # close
        await browser.close()


if __name__ == "__main__":
    try:
      log = helpers.init_logger(log_level="info")
      log.info("Script started.")
    except Exception as e:
        print(f"Failed to initiate logger.")
        print(e)
        helpers._terminate_script(1)

    main()
