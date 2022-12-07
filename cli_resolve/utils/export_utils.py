from datetime import datetime, timedelta
import csv
import pandas as pd


def get_filename(date_str):
    """
    Takes MM/DD/YYYY date string and returns MM-DD-YYYY string to be used in filenames
    :param date_str:
    :return:
    """
    return "-".join(date_str.split("/"))


def get_res_fieldnames(res_dict, start_date_str, end_date):
    res_fields = []
    for res_id, entry in res_dict.items():
        log_data = entry["data"]
        has_data = check_data_against_range(log_data, start_date_str, end_date)
        if has_data:
            res_fields.append(res_id)
    return res_fields


def check_data_against_range(data, start_date_str, end_date):
    curr_date = datetime.strptime(start_date_str, "%m/%d/%Y")
    while curr_date <= end_date:
        curr_date_str = datetime.strftime(curr_date, "%-m/%-d/%Y")
        if curr_date_str in data:
            # We're happy as long as there's a single date with data
            return True
        curr_date += timedelta(days=1)
    return False


def write_new_csv_with_header(fieldnames, fname_start, fname_end):
    with open(f"data/exports/res_{fname_start}_{fname_end}.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()


def write_res_row(fieldnames, curr_data, fname_start, fname_end):
    with open(f"data/exports/res_{fname_start}_{fname_end}.csv", "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writerow(curr_data)


def get_years(start_date_str, end_date_str):
    start_yr = int(start_date_str.split("/")[2])
    end_yr = int(end_date_str.split("/")[2])
    return end_yr - start_yr + 1


def clean_for_graphing(filepath):
    print("*** Cleaning data")
    filename = filepath.split("data/exports/")[1]
    df = pd.read_csv(filepath)
    data_start = 1
    data_end = len(df.columns) - 1

    # TODO: make this DRY (compare with convert_legacy_resolutions)
    df[['Month', 'Day', 'Year']] = df['date'].str.split('/', expand=True)

    df['Month'] = df['Month'].astype(int)
    df['Day'] = df['Day'].astype(int)
    df['Year'] = df['Year'].astype(int)

    # Replace falsy values with 0's, otherwise the boolean conversion will return True for "0" and "0.0"
    df.fillna(0, inplace=True)
    df = df.replace('0', 0)
    df = df.replace('0.0', 0)
    df = df.replace('False', 0)
    df = df.replace('True', 1)

    # Create new column that sums up total resolutions met per day
    resolution_bools = df.iloc[:, data_start:data_end + 1].astype(bool)
    df['Resolutions Met'] = resolution_bools.sum(axis=1)

    # Create new boolean columns from categorical resolutions
    start = data_start
    while start < data_end + 1:
        end = start + 1
        col_name = df.iloc[:, start:end].columns.values[0]
        df[f"{col_name}_bool"] = df.iloc[:, start:end].astype(bool)
        df[f"{col_name}_bool"] = df[f"{col_name}_bool"].astype(int)
        start += 1

    # Save cleaned df as CSV
    df.to_csv(f"data/cleaned/{filename}", index=False)
