import re
import logging
from src.models.kiara_work_item import KiaraWorkItem

log = logging.getLogger(__name__)

async def _format_date_silly(date: str):
    date_parts = date.split("-")
    date_parts = [re.sub(r"^0", "", part) for part in date_parts]
    return f"{date_parts[1]}-{date_parts[2]}"


async def _format_timespan_silly(time_spent: float):
    """valid input: integers + 0.25 | 0.5 | 0.75"""
    hours = int(time_spent)
    minutes = int((time_spent % 1) * 60)
    return f"{hours}.{minutes}"

def is_empty_value(work_item: KiaraWorkItem, work_item_key: str) -> bool:
    if getattr(work_item, work_item_key):
        log.debug(getattr(work_item, work_item_key))
        log.debug(f"{work_item_key} is not empty for work item '{work_item.description}'")
        return True
    else:
        log.debug(f"{work_item_key} is empty for work item '{work_item.description}'")
        return False