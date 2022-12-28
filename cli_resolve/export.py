from utils.resolution_utils import get_all_resolutions
from utils.export_utils import *
from utils.graph_utils import *
from utils.menu_utils import *

INSTRUCTIONS = "Enter the start and end dates ('MM/DD/YYYY') for which you would like to make an export.\n" \
               "--if you specify only the year, all data from that year will be included\n" \
               "e.g. start_date='2020' and end_date='2021' exports all data from 1/1/2020 to 12/31/2021\n"
GRAPH_INSTRUCTIONS = "--enter 'file' to load a dataset from file"


def export_csv(start_date_str=None, end_date_str=None):
    """
    Export CSV from app data.
    """
    print("*** Exporting CSV")
    # User input is requested if this function is not called from export_graph()
    if not start_date_str or not end_date_str:
        print(f"INSTRUCTIONS: {INSTRUCTIONS}")
        start_date_str = handle_input(prompt="start date: ", response_type="datestring", year_start=True)
        end_date_str = handle_input(prompt="end date: ", response_type="datestring", year_end=True)

    fname_start = get_filename(start_date_str)
    fname_end = get_filename(end_date_str)

    # Check whether there's already a CSV for the time range of interest
    if os.path.exists(f"data/exports/res_{fname_start}_{fname_end}.csv"):
        print(f"There is already a CSV file for start={start_date_str} end={end_date_str}.")
        override = handle_input(prompt="Save over existing file? (Y/N): ", response_type="boolean")
        if not override:
            return go_home_message()

    print(f"*** Exporting data: {start_date_str} - {end_date_str}")

    # Get a list of the resolutions that have any data within the time range of interest
    curr_date_str = start_date_str
    curr_date = datetime.strptime(curr_date_str, "%m/%d/%Y")
    end_date = datetime.strptime(end_date_str, "%m/%d/%Y")

    all_res_dict = get_all_resolutions()

    fieldnames = ["date"]
    res_fields = get_res_fieldnames(all_res_dict, start_date_str, end_date)
    if len(res_fields) < 1:
        print(f"Found no data from {start_date_str} to {end_date_str}")
        return go_home_message()
    fieldnames = fieldnames + res_fields

    write_new_csv_with_header(fieldnames, fname_start, fname_end)
    # Go through all the resolutions that have some data for the date range and write the CSV row-by-row
    while curr_date <= end_date:
        curr_data = {"date": curr_date_str}
        for res in res_fields:
            log_data = all_res_dict[res]["data"]
            try:
                data_on_date = log_data[curr_date_str]
                if data_on_date is False:
                    datapoint = {res: 0}
                elif data_on_date is True:
                    datapoint = {res: 1}
                else:  # non-boolean value
                    datapoint = {res: data_on_date}
                print(f"*** Data found for resolution={res} on date={curr_date_str}!")
            except KeyError:
                print(f"resolution={res} does not have data for date={curr_date_str}, recording as 0")
                datapoint = {res: 0}
            curr_data.update(datapoint)
        write_res_row(fieldnames, curr_data, fname_start, fname_end)
        curr_date += timedelta(days=1)
        curr_date_str = datetime.strftime(curr_date, "%-m/%-d/%Y")


def export_graph():
    """
    Generate and export heatmaps from app data.
    """
    print(f"INSTRUCTIONS: {INSTRUCTIONS}{GRAPH_INSTRUCTIONS}")
    start_date_str = handle_input(prompt="start date: ", response_type="datestring", year_start=True)
    if start_date_str == "file":
        return export_graph_from_file()
    end_date_str = handle_input(prompt="end date: ", response_type="datestring", year_end=True)
    years_list = get_years_list(start_date_str, end_date_str)

    display_events = handle_input(prompt="Do you want event data overlaid on this graph? (Y/N): ",
                                  response_type="boolean")
    if display_events:
        event_type = handle_input(prompt="What type of events? ")
    else:
        event_type = None
    export_minimaps = handle_input(prompt="Do you want minimaps for select resolutions? (Y/N): ",
                                   response_type="boolean")

    fname_start = get_filename(start_date_str)
    fname_end = get_filename(end_date_str)

    # Generate graph from existing cleaned CSV, or export a CSV first and then generate graph
    cleaned_filepath = f"data/cleaned/res_{fname_start}_{fname_end}.csv"
    exports_filepath = f"data/exports/res_{fname_start}_{fname_end}.csv"

    already_cleaned = os.path.exists(cleaned_filepath)

    if already_cleaned:
        last_generated_ts = datetime.fromtimestamp(os.path.getmtime(cleaned_filepath))
        regenerate = handle_input(
            prompt=f"Clean data for this graph last generated {last_generated_ts}. Do you want to rerun? (Y/N): ",
            response_type="boolean"
        )
        if not regenerate:
            generate_heatmap(cleaned_filepath, years_list=years_list, notable_days=event_type)
            if export_minimaps:
                generate_minimaps(cleaned_filepath, years_list=years_list)
            plt.show()
    if not already_cleaned or regenerate:
        export_csv(start_date_str, end_date_str)
        clean_for_graphing(exports_filepath)
        generate_heatmap(cleaned_filepath, years_list=years_list, notable_days=event_type)
        if export_minimaps:
            generate_minimaps(cleaned_filepath, years_list=years_list)
        plt.show()
