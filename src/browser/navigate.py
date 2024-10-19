import logging

from playwright.async_api import (
    Page,
    Locator,
    TimeoutError as PlaywrightTimeoutError,
    Error as PlaywrightError,
)

from src.browser.locate import get_section_expand_collapse_button, get_target_element
from src.exceptions.custom_exceptions import (
    BrowserNavigationError,
    TargetElementNotFoundError,
    KiaraAutomationError,
)

log = logging.getLogger(__name__)


async def open_timesheet_page(page: Page) -> None:
    identifier = "Open timesheet page button"
    try:
        log.debug("Opening timesheet page.")
        open_timesheet_locator = await get_target_element(
            locator=page.get_by_role("cell", name="knop ga verder").locator("a"),
            element_identifier=identifier,
        )
        if open_timesheet_locator:
            await click_navigation_button(
                nav_button_locator=open_timesheet_locator, nav_button_name=identifier
            )
            log.info("Navigated to timesheet page.")
        else:
            raise TargetElementNotFoundError(f"{identifier} not found.")
    except KiaraAutomationError as e:
        log.warning(
            "Failed to navigate to timesheet page. "
            "Ensure you're on the landing page after ACM/IDM authentication."
        )
        raise BrowserNavigationError from e


async def expand_collapse_section(
    page: Page, search_string: str, collapse: bool
) -> None:
    button_locator = await get_section_expand_collapse_button(
        page=page, search_string=search_string, collapse=collapse
    )
    try:
        await button_locator.click()
        log.info(
            f"{'Collapsed' if collapse else 'Expanded'} section '{search_string}'."
        )
    except PlaywrightTimeoutError as e:
        log.error(f"Failed to collapse or expand section. {e}")


async def navigate_to_page(page: Page, url: str):
    try:
        await page.goto(url)
        log.info(f"Opened page: {url}")
    except (PlaywrightTimeoutError, PlaywrightError) as e:
        log.error(f"Failed to open page: {url}. {e}")
        raise BrowserNavigationError from e


async def click_navigation_button(
    nav_button_locator: Locator, nav_button_name: str, timeout: int = 3000
):
    try:
        await nav_button_locator.click(timeout=timeout)
        log.info(f"Clicked navigation button: '{nav_button_name}'")
    except PlaywrightTimeoutError as e:
        log.error(f"Failed to click navigation button: '{nav_button_name}'")
        raise BrowserNavigationError from e


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
