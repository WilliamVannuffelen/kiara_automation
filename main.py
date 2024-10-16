import asyncio
import logging

from src.config.input import get_args
from src.config.read_config import read_config
from src.exceptions.custom_exceptions import InputDataProcessingError
from src.flow_control.controllers import process_input_data, run_browser_automation
from src.lib.helpers import _terminate_script, init_logging


def main(input_file_name: str, input_sheet_name: str) -> None:
    try:
        projects = process_input_data(input_file_name, input_sheet_name)
    except InputDataProcessingError as e:
        log.error(f"Terminating error. Details: '{e}'.")
        _terminate_script(1)
    asyncio.run(run_browser_automation(projects))


if __name__ == "__main__":
    config_values = read_config()
    file_name, sheet_name = get_args()

    init_logging(log_level=config_values.get("log_level", "info"))
    try:
        log = logging.getLogger(__name__)
        log.info("Script started.")
    except Exception as e:
        print(f"Failed to initiate logger: '{e}'.")
        _terminate_script(1)

    file_name = file_name if file_name else config_values.get("input_file", None)
    if not file_name:
        log.error(
            "No input file name provided. Either update the config file or pass it as a command line argument."
        )
        _terminate_script(1)
    main(input_file_name=file_name, input_sheet_name=sheet_name)
