import logging
from bisect import bisect

logging.GROUP = 21
logging.SECTION = 22
logging.COMMAND = 23
logging.ENDGROUP = 24
logging.addLevelName(logging.GROUP, "GROUP")
logging.addLevelName(logging.SECTION, "SECTION")
logging.addLevelName(logging.COMMAND, "COMMAND")
logging.addLevelName(logging.ENDGROUP, "ENDGROUP")


class AzureDevOpsLogFormatter(logging.Formatter):
    def __init__(self):
        self.formats_dict = {
            logging.DEBUG: "##[debug]       %(asctime)s - DEBUG - %(name)s - %(module)s.%(funcName)s - %(message)s",
            logging.INFO: "                %(asctime)s - INFO  - %(name)s - %(module)s.%(funcName)s - %(message)s",
            logging.WARNING: "##[warning]     %(asctime)s - WARN  - %(name)s - %(module)s.%(funcName)s - %(message)s",
            logging.ERROR: "##[error]       %(asctime)s - ERROR - %(name)s - %(module)s.%(funcName)s - %(message)s",
            logging.GROUP: "##[group] %(message)s",
            logging.SECTION: "##[section]              %(message)s",
            logging.COMMAND: "##[command]              %(asctime)s - %(levelname)s - %(name)s - %(module)s.%(funcName)s - %(message)s",
            logging.ENDGROUP: "##[endgroup] %(message)s",
        }
        self.formats = sorted(
            (level, logging.Formatter(fmt)) for level, fmt in self.formats_dict.items()
        )
        super().__init__()

    def format(self, record: logging.LogRecord) -> str:
        idx = bisect(self.formats, (record.levelno,), hi=len(self.formats) - 1)
        level, formatter = self.formats[idx]
        return formatter.format(record)


class AzureDevopsLogger(logging.getLoggerClass()):
    def __init__(self, name):
        logging.Logger.__init__(self, name)

    def group(self, *args, **kwargs):
        self.log(logging.GROUP, "", *args, **kwargs)

    def section(self, msg, *args, **kwargs):
        self.log(logging.SECTION, msg, *args, **kwargs)

    def command(self, msg, *args, **kwargs):
        self.log(logging.COMMAND, msg, *args, **kwargs)

    def endgroup(self, *args, **kwargs):
        self.log(logging.ENDGROUP, "", *args, **kwargs)
