import logging
import argparse
from datetime import datetime, timedelta

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