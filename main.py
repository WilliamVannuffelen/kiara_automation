import asyncio
import logging

from src.config.input import get_args
from src.exceptions.custom_exceptions import InputDataProcessingError
from src.flow_control.controllers import process_input_data, run_browser_automation
from src.lib.helpers import _terminate_script, init_logging


def main():
    file_name, sheet_name = get_args()

    try:
        projects = process_input_data(file_name, sheet_name)
    except InputDataProcessingError as e:
        log.error(f"Terminating error. Details: '{e}'.")
        _terminate_script(1)
    asyncio.run(run_browser_automation(projects))


if __name__ == "__main__":
    init_logging(log_level="debug")
    try:
        log = logging.getLogger(__name__)
        log.info("Script started.")
    except Exception as e:
        print(f"Failed to initiate logger: '{e}'.")
        _terminate_script(1)

    main()
