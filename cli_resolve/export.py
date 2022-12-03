import os

from utils.resolution_utils import get_all_resolutions
from utils.export_utils import *


def export_csv(start_date=None, end_date=None):
    if start_date is None or end_date is None:
        instructions = "Enter the start and end dates ('MM/DD/YYYY') for which you would like to make an export.\n" \
                       "If you specify only the year, all data from that year will be included.\n" \
                       "e.g. start_date='2020' and end_date='2021' exports all data from 1/1/2020 to 12/31/2021\n"
        print(instructions)
        start_date_str = input("start date: ")
        end_date_str = input("end date: ")
    else:
        start_date_str = start_date
        end_date_str = end_date

    fname_start = "-".join(start_date_str.split("/"))
    fname_end = "-".join(end_date_str.split("/"))
    if len(start_date_str) == 4:
        fname_start = start_date_str
        start_date_str = f"1/1/{start_date_str}"
    if len(end_date_str) == 4:
        fname_end = end_date_str
        end_date_str = f"12/31/{end_date_str}"

    # Check whether there's already a CSV for the time range of interest
    if os.path.exists(f"data/exports/res_{fname_start}_{fname_end}.csv"):
        override = input(f"There is already a CSV file for start={start_date_str} end={end_date_str}.\n"
                         f"Save over existing file? ('Y' to continue, anything else to return to menu): ").upper()
        if override != "Y":
            return

    print(f"*** Exporting data: {start_date_str} - {end_date_str}")

    # Check that there's at least one resolution with data
    curr_date_str = start_date_str
    curr_date = datetime.strptime(curr_date_str, "%m/%d/%Y")
    end_date = datetime.strptime(end_date_str, "%m/%d/%Y")

    all_res_dict = get_all_resolutions()
    fieldnames = ["date"]
    # Narrow down the resolutions that have any data within the time range of interest
    res_fields = get_res_fieldnames(all_res_dict, start_date_str, end_date)
    fieldnames = fieldnames + res_fields

    while curr_date <= end_date:
        curr_data = {"date": curr_date_str}
        for res in res_fields:
            log_data = all_res_dict[res]["data"]
            try:
                datapoint = {res: log_data[curr_date_str]}
                print(f"*** Data found for resolution={res} on date={curr_date_str}!")
            except KeyError as e:
                print(f"resolution={res} does not have data for date={curr_date_str}, recording as 0")
                datapoint = {res: 0}
            curr_data.update(datapoint)
        write_res_row(fieldnames, curr_data, fname_start, fname_end)
        curr_date += timedelta(days=1)
        curr_date_str = datetime.strftime(curr_date, "%-m/%-d/%Y")


def export_graph():
    # TODO: make this DRY
    instructions = "Enter the start and end dates ('MM/DD/YYYY') for which you would like to make an export.\n" \
                   "If you specify only the year, all data from that year will be included.\n" \
                   "e.g. start_date='2020' and end_date='2021' exports all data from 1/1/2020 to 12/31/2021\n"
    print(instructions)
    start_date_str = input("start date: ")
    end_date_str = input("end date: ")

    fname_start = "-".join(start_date_str.split("/"))
    fname_end = "-".join(end_date_str.split("/"))
    if len(start_date_str) == 4:
        fname_start = start_date_str
    if len(end_date_str) == 4:
        fname_end = end_date_str

    # Generate graph from existing CSV, or export a CSV first and then generate graph
    cleaned_filepath = f"data/cleaned/res_{fname_start}_{fname_end}.csv"
    exports_filepath = f"data/exports/res_{fname_start}_{fname_end}.csv"
    # TODO: add flag to force new export and conversion (otherwise data will be stale)
    if os.path.exists(cleaned_filepath):
        print("*** Generating heatmap from existing CSV")
    elif os.path.exists(exports_filepath):
        print("*** Cleaning data")
        convert_resolutions(exports_filepath)
        print("*** Generating heatmap")
    else:
        print("*** Exporting CSV")
        export_csv(start_date_str, end_date_str)
        print("*** Cleaning data")
        convert_resolutions(exports_filepath)
        print("*** Generating heatmap")
    generate_heatmap(cleaned_filepath)

