import logging

from src.input.prep_data import (
    convert_to_work_item,
    group_work_items,
    read_input_file,
    truncate_dataframe,
    validate_df_columns,
)

from src.objects.kiara_project import KiaraProject
from src.exceptions.custom_exceptions import InputDataProcessingError

log = logging.getLogger(__name__)


def process_input_data(file_name: str, sheet_name: str) -> list[KiaraProject]:
    try:
        df = read_input_file(file_name, sheet_name)
        df = truncate_dataframe(df)
        validate_df_columns(df)
        work_items = convert_to_work_item(df)
        projects = group_work_items(work_items)
        return projects
    except Exception as e:
        raise InputDataProcessingError(
            f"Failed to process input data: '{type(e)}'"
        ) from e
