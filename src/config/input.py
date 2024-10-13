import logging
import argparse
from datetime import datetime, timedelta
import math
from itertools import groupby
import pandas as pd

log = logging.getLogger(__name__)


def get_datetime_week_start() -> str:
    log.info("Getting the start of the current week to set default sheet name.")
    today = datetime.today()
    days_to_monday = today.weekday()
    monday = today - timedelta(days=days_to_monday)
    return monday.strftime("%Y-%m-%d")

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--file_name","-f",
        type=str,
        help="The name of the input Excel file.",
        required=False,
        #default="timsheet (version 2) (version 2) (version 2) (version 1)(AutoRecovered) OK-2024(AutoRecovered).xlsx", # lol
        default="~/wvl/devel/tempo/t_upload.xlsx"
    )
    parser.add_argument(
        "--sheet_name","-s",
        type=str,
        help="The name of the excel sheet to read from.",
        required=False,
        default=None,
    )
    args = parser.parse_args()
    file_name = args.file_name
    sheet_name = args.sheet_name if args.sheet_name else get_datetime_week_start()

    log.debug(f"Provided file name: '{file_name}'")
    log.debug(f"Provided sheet name: '{sheet_name}'")
    log.info("Parsed provided arguments.")

    return file_name, sheet_name


def read_input_file(file_name: str, sheet_name: str):
    try:
        df = pd.read_excel(io=file_name, sheet_name=sheet_name, usecols="A:F")
        log.info(f"Read input file '{file_name}' - sheet '{sheet_name}'.")
    except FileNotFoundError as e:
        log.error(f"File '{file_name}' not found.")
        raise e
    except Exception as e:
        log.error(f"Error reading file '{file_name}'.")
        raise e
    return df.to_dict("records")


def add_project_column(work_items: list, project: str = "CS0126444 - Wonen Cloudzone - dedicated operationeel projectteam"):
    """if unspecified, set default project"""
    for work_item in work_items:
        if (isinstance(work_item["Project"], float) and math.isnan(work_item["Project"])) or work_item["Project"] == "":
            log.debug(f"Adding default project '{project}' to work item '{work_item['Description']}'.")
            work_item["Project"] = project
    return work_items


def add_dummy_jira_ref(work_items: list):
    for work_item in work_items:
        if pd.isna(work_item["JiraRef"]):
            work_item["JiraRef"] = ""
    return work_items


def split_projects(work_items: list):
    grouped_work_items = sorted(work_items, key=lambda x: x["Project"])
    grouped_work_items = {k: list(v) for k, v in groupby(grouped_work_items, key=lambda x: x["Project"])}

    for k, v in grouped_work_items.items():
        log.info(f"Input contains project '{k}' with {len(v)} work items.")
    return grouped_work_items