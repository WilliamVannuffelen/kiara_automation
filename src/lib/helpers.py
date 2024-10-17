import logging
import sys

from src.objects.logging import ExceptionDebugStackTraceHandler

log = logging.getLogger(__name__)


def init_logging(
    log_level: str = "info",
) -> None:
    stream_handler = ExceptionDebugStackTraceHandler()

    log_levels = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }

    logging.basicConfig(
        format="%(asctime)20s - %(levelname)s - %(name)s.%(funcName)s - %(message)s",
        handlers=[stream_handler],
        level=log_levels.get(log_level.lower(), logging.INFO),
    )
    log.debug("Logger init done.")


def terminate_script(exit_code: int) -> None:
    exit_desc = "Unknown"
    if exit_code == 0:
        exit_desc = "Clean exit"
    elif exit_code == 1:
        exit_desc = "Fatal error"
    log.info(f"Script ended. Reason: {exit_desc}.")
    sys.exit(exit_code)
