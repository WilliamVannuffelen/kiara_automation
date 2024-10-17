import logging

import pandas as pd

from src.exceptions.custom_exceptions import (
    DataFrameFirstNanIndexTypeError,
    InputFileLoadError,
    InvalidDataFrameColumnsError,
)
from src.objects.kiara_project import KiaraProject
from src.objects.kiara_work_item import KiaraWorkItem

log = logging.getLogger(__name__)


def read_input_file(file_name: str, sheet_name: str) -> pd.DataFrame:
    try:
        df = pd.read_excel(io=file_name, sheet_name=sheet_name, usecols="A:G")
        log.info(f"Read input file '{file_name}' - sheet '{sheet_name}'.")
    except FileNotFoundError as e:
        log.exception(f"File '{file_name}' not found: {e}.")
        raise InputFileLoadError from e
    except ValueError as e:
        log.exception(f"Failed to load input data: {e}.")
        raise InputFileLoadError from e
    except Exception as e:
        log.exception("Failed to load input data.")
        raise InputFileLoadError from e
    return df


def truncate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if not df["Description"].isna().any():
        log.debug("No NaN values found in 'Description' column. No need to truncate.")
        return df
    first_nan_index = df["Description"].isna().idxmax()
    try:
        df = df.iloc[:first_nan_index]
        log.debug(f"Truncated DataFrame at index '{first_nan_index}'.")
    except ValueError as e:
        log.exception(
            "First NaN index in 'Description' column is not an integer: '{first_nan_index}'"
        )
        raise DataFrameFirstNanIndexTypeError from e
    return df


def validate_df_columns(df: pd.DataFrame) -> None:
    expected_columns = [
        "Day",
        "Project",
        "Description",
        "JiraRef",
        "AppRef",
        "Date",
        "TimeSpent",
    ]

    df.columns = df.columns.str.strip()

    if set(df.columns) != set(expected_columns):
        log.exception(
            f"Columns in DataFrame do not match expected columns: '{df.columns}'"
        )
        raise InvalidDataFrameColumnsError
    log.debug("DataFrame columns validated.")


def convert_to_work_item(df: pd.DataFrame) -> list[KiaraWorkItem]:
    work_items = []
    for _, row in df.iterrows():
        work_item = KiaraWorkItem(
            day=row["Day"],
            project=row["Project"],
            description=row["Description"],
            jira_ref=row["JiraRef"],
            app_ref=row["AppRef"],
            date=row["Date"],
            time_spent=row["TimeSpent"],
        )
        work_items.append(work_item)
    return work_items


def group_work_items(work_items: list[KiaraWorkItem]) -> list[KiaraProject]:
    projects = {}
    for work_item in work_items:
        project_name = work_item.project
        if project_name not in projects:
            projects[project_name] = KiaraProject(project_name)
        projects[project_name].add_work_item(work_item)
    return list(projects.values())
