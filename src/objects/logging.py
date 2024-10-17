import logging


class ExceptionDebugStackTraceHandler(logging.StreamHandler):
    """
    Logging handler that ensures that stack traces are only printed for log.exception() if log level is DEBUG.
    """

    def emit(self, record):
        if (
            record.levelno == logging.ERROR
            and record.exc_info is None
            and logging.getLogger().level == logging.DEBUG
        ):
            record.exc_info = None  # Ensure exc_info is None for log.error()
        elif (
            record.levelno == logging.ERROR
            and record.exc_info
            and logging.getLogger().level != logging.DEBUG
        ):
            record.exc_info = (
                None  # Ensure exc_info is None for log.exception() unless debug level
            )
        super().emit(record)
