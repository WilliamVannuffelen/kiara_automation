import logging
import sys
from typing import Optional

from src.objects.logging import ExceptionDebugStackTraceHandler

log = logging.getLogger(__name__)


def init_logging(
    log_level: Optional[str],
) -> None:
    stream_handler = ExceptionDebugStackTraceHandler()

    log_levels = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    try:
        logging.basicConfig(
            format="%(asctime)20s - %(levelname)s - %(name)s.%(funcName)s - %(message)s",
            handlers=[stream_handler],
            level=log_levels.get(
                log_level.lower() if log_level else "info", logging.INFO
            ),
        )
        log.debug("Logger init done.")
    except (OSError, ValueError, FileNotFoundError) as e:
        print(f"Failed to initiate logger: '{e}'.")
        raise e


def terminate_script(exit_code: int) -> None:
    exit_desc = "Unknown"
    if exit_code == 0:
        exit_desc = "Clean exit"
    elif exit_code == 1:
        exit_desc = "Fatal error"
    message = f"Script ended. Reason: {exit_desc}."
    try:
        log.info(message)
    except (OSError, ValueError, FileNotFoundError):
        print(f"Failed to log termination message: '{message}'.")
        print(message)
    sys.exit(exit_code)
