import asyncio
import logging
from typing import Dict

from src.config.input import get_args
from src.config.read_config import read_config
from src.exceptions.custom_exceptions import (
    InputDataProcessingError,
    ConfigFileProcessingError,
    BrowserNavigationError,
)
from src.flow_control.controllers import process_input_data, run_browser_automation
from src.lib.helpers import terminate_script, init_logging
from src.objects.kiara_project import KiaraProject

log: logging.Logger = logging.getLogger(__name__)


def main(
    input_file_name: str, input_sheet_name: str, input_config_values: Dict[str, str]
) -> None:
    projects: list[KiaraProject] = []
    try:
        projects = process_input_data(input_file_name, input_sheet_name)
    except InputDataProcessingError as e:
        log.error(f"Terminating error: '{type(e.__cause__).__name__}'.")
        terminate_script(1)
    try:
        asyncio.run(
            run_browser_automation(
                input_config_values=input_config_values, projects=projects
            )
        )
    except BrowserNavigationError as e:
        log.error(f"Terminating error: '{type(e).__name__}'.")
        terminate_script(1)


if __name__ == "__main__":
    config_values: Dict[str, str] = {}

    try:
        config_values = read_config()
    except ConfigFileProcessingError as e:
        print(f"Failed to read config file: '{e}'.")
        terminate_script(1)
    file_name, sheet_name = get_args()

    try:
        init_logging(log_level=config_values.get("log_level", "info"))
    except (OSError, ValueError, FileNotFoundError) as e:
        print(f"Failed to initiate logger: '{e}'.")
        terminate_script(1)

    file_name = file_name if file_name else config_values.get("input_file", None)
    if not file_name:
        log.error(
            "No input file name provided. "
            "Either update the config file or pass it as a command line argument."
        )
        terminate_script(1)
    else:
        main(
            input_file_name=file_name,
            input_sheet_name=sheet_name,
            input_config_values=config_values,
        )
