import logging
from logging import Logger
from lib.ado_logging import AzureDevOpsLogFormatter, AzureDevopsLogger
import sys
import os

log = logging.getLogger("main")


def init_logger(
    log_class: str = "default", log_formatter: str = "default", log_level: str = "info"
) -> Logger:
    match log_class.lower():
        case "azuredevops":
            logging.setLoggerClass(AzureDevopsLogger)
        case _:
            pass

    match log_formatter.lower():
        case "azuredevops":
            stream_handler = logging.StreamHandler()
            stream_handler.setFormatter(AzureDevOpsLogFormatter())
        case _:
            stream_handler = logging.StreamHandler()

    logging.basicConfig(
        format="%(asctime)20s - %(levelname)s - %(name)s - %(module)s.%(funcName)s - %(message)s",
        handlers=[stream_handler],
    )
    log = logging.getLogger("main")

    match log_level.lower():
        case "debug":
            log.setLevel(logging.DEBUG)
        case "info":
            log.setLevel(logging.INFO)
        case "warning":
            log.setLevel(logging.WARNING)
        case "error":
            log.setLevel(logging.ERROR)
        case "critical":
            log.setLevel(logging.CRITICAL)
        case _:
            log.setLevel(logging.INFO)

    log.debug("Logger init done.")
    return log


def _terminate_script(exit_code: int) -> None:
    if exit_code == 0:
        exit_desc = "Clean exit"
    elif exit_code == 1:
        exit_desc = "Fatal error"
    try:
        log.info(f"Script ended. Reason: {exit_desc}.")
    except Exception as e:
        print(f"Script ended. Reason: {exit_desc}.")
    sys.exit(exit_code)


def get_env_var(env_var: dict) -> str:
    try:
        evar = os.environ[env_var["name"]]
        log.debug(f"Found environment variable: {env_var['name']}.")
    except KeyError as e:
        if env_var["required"] == True:
            log.error("Missing mandatory environment variable: {}.")
            help._terminate_script(1)
        else:
            evar = None
            log.debug(f"Optional environment variable not found: '{env_var['name']}'.")
    return evar
