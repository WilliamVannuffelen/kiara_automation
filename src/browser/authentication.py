import re
import logging
from playwright.async_api import Page
from src.browser.navigate import navigate_to_page, click_navigation_button
from src.browser.locate import (
    get_authentication_method_button,
    get_phone_number_input_box,
    get_target_element,
)
from src.browser.update import enter_cell_text_generic
from src.exceptions.custom_exceptions import (
    BrowserNavigationError,
    TargetElementNotFoundError,
    BrowserFillCellError,
)

log = logging.getLogger(__name__)


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
