import re
import logging
from src.models.kiara_work_item import KiaraWorkItem

log = logging.getLogger(__name__)


def is_empty_value(work_item: KiaraWorkItem, work_item_key: str) -> bool:
    if getattr(work_item, work_item_key):
        log.debug(getattr(work_item, work_item_key))
        log.debug(f"{work_item_key} is not empty for work item '{work_item.description}'")
        return True
    else:
        log.debug(f"{work_item_key} is empty for work item '{work_item.description}'")
        return False