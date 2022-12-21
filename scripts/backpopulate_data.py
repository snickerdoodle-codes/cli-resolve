import pandas as pd
import os
import sys
import json
from datetime import datetime
import shutil

from cli_resolve.utils.input_utils import *

# INPUTS
filename = "nyr22_partial.csv"


def get_resolution_choice_set(df):
    non_options = ["date", "Month", "Day", "Year", "Resolutions Met"]
    return [x for x in df if x not in non_options and "bool" not in x]


def get_resolution_columns_and_values(df):
    choice_set = get_resolution_choice_set(df)
    options = ""
    for col in choice_set:
        values = df[col].unique()
        options += "{0:20}  {1}".format(col, values)
        options += "\n"
    return options


def get_columns(prompt, df):
    cols = input(prompt)
    cols = "".join(cols.split())  # remove whitespace
    all_options = get_resolution_choice_set(df)

    if cols.lower() == "all":
        return all_options

    col_list = cols.split(",")
    col_list = [x for x in col_list if x]  # remove empty elements
    validated_list = []
    for col in col_list:
        if col not in all_options:
            print(f"`{col}` is not a valid column -- removing from list to generate minimaps from")
        else:
            validated_list.append(col)
    return validated_list


# Read the CSV
filepath = f"../data/cleaned/{filename}"
if not os.path.exists(filepath):
    sys.exit(f"filepath={filepath} does not exist")

df = pd.read_csv(filepath)
options = get_resolution_columns_and_values(df)
print(f"Preview of data from uploaded dataset:\n{options}\n")

instructions = "Enter a comma-separated list of columns containing resolution data (e.g. exercise,skincare).\n" \
               "Enter 'all' to use all columns.\n"
print(f"INSTRUCTIONS: {instructions}")
col_list = []
while len(col_list) == 0:
    col_list = get_columns(
        "Which resolutions do you want to backpopulate?: ",
        df
    )

# Load app data
with open("../data/resolutions.json", "r") as f:
    app_data = json.load(f)

# Loop through each resolution column
days = len(df)
curr_day = 0
curr_col = 0
data_end = len(col_list) - 1

while curr_col <= data_end:
    col_name = col_list[curr_col]
    print(f"*** Adding data from resolution={col_name}")

    # Check whether this resolution already exists in app data
    exists = col_name.lower() in app_data
    first_date = df["date"][0]
    last_date = df["date"][days - 1]

    if exists:
        merge_data = handle_input(prompt=f"res={col_name} already exists. Merge with existing data? (Y/N): ",
                                  response_type="boolean")
        if merge_data:
            print(f"*** Merging res={col_name}")
            res_id = col_name.lower()
            is_binary = app_data[res_id]["is_binary"]

            # Calculate res_creation_date (first date entry from current data OR res_creation_date of existing
            # resolution, whichever is earlier)
            first_date_dt = datetime.strptime(first_date, "%m/%d/%Y")
            exist_creation_date = app_data[res_id]["res_creation_date"]
            exist_creation_date_dt = datetime.strptime(exist_creation_date, "%m/%d/%Y")
            res_creation_date = first_date if first_date_dt < exist_creation_date_dt else exist_creation_date

            # Expiration is last date entry from current data OR res_expiration_date of existing resolution,
            # whichever is later
            last_date_dt = datetime.strptime(last_date, "%m/%d/%Y")
            exist_expiration_date = app_data[res_id]["res_expiration_date"]
            if exist_expiration_date is not None:
                exist_expiration_date_dt = datetime.strptime(exist_expiration_date, "%m/%d/%Y")
                res_expiration_date = last_date if last_date_dt > exist_expiration_date_dt else exist_expiration_date
            else:
                res_expiration_date = exist_expiration_date

            app_data[res_id].update(
                {
                    "res_creation_date": res_creation_date,
                    "res_expiration_date": res_expiration_date,
                }
            )

    # New resolution without precedent
    if (not exists) or (not merge_data):
        if exists:
            res_id = handle_input(f"Let's give this resolution a new res_id to differentiate it from {col_name}: ")
        else:
            keep_name = handle_input(prompt=f"Want to keep the res_id `{col_name}`? (Y/N): ", response_type="boolean")
            if keep_name:
                res_id = col_name
            else:
                res_id = handle_input("Let's give this resolution a new res_id: ")
        print(f"*** Creating a new resolution res={res_id}")
        res_descript = handle_input("Provide a short description for this resolution: ")
        res_creation_date = df.loc[[0], "date"].values[0]  # first date entry from current data
        is_active = handle_input(prompt="Is this an active resolution? (Y/N): ", response_type="boolean")
        is_expired = handle_input(prompt=f"Did this resolution expire on {last_date}? (Y/N): ", response_type="boolean")
        if is_expired:
            res_expiration_date = last_date
        else:
            res_expiration_date = handle_input(
                prompt="When does this resolution expire? ('MM/DD/YYYY' or 'never' for no expiration): ",
                response_type="datestring"
            )
        is_binary = handle_input(
            prompt="Is this resolution's outcome binary? (Y/N): ",
            response_type="boolean",
            instructions="Binary outcomes tell us whether or not you did something, while categorical outcomes "
                         "tell us about the kind of thing you did.\n"
                         "For example, for the resolution to exercise, "
                         "a binary outcome is exercising, or not exercising. "
                         "In contrast, a categorical outcome names the kind of exercise you did (e.g. "
                         "run/bike/swim). "
        )

        res = {
            "res_descript": res_descript,
            "res_creation_date": res_creation_date,
            "is_active": is_active,
            "res_expiration_date": res_expiration_date,
            "is_binary": is_binary,
            "res_detail_codes": {},
            "data": {},
        }
        app_data[res_id] = res

    # Populate the data dict for both merged and new resolutions
    print("*** Backpopulating resolutions data")
    detail_codes = app_data[res_id]["res_detail_codes"]
    code_translator = {}  # keep track of recoded datapoints

    while curr_day < days:
        datapoint = df.loc[[curr_day], col_name].values[0]
        if not datapoint or datapoint == "0" or datapoint == "0.0":  # binary and non-binary falsy value
            datapoint = False
        if is_binary:
            if datapoint:  # binary truthy value
                datapoint = True
        else:
            if datapoint:  # non-binary truthy value
                # Check the translator first to see if previously encountered
                datapoint = code_translator.get(datapoint, datapoint)
                # Add to detail codes if seeing for first time
                if datapoint not in detail_codes:
                    keep_code = handle_input(prompt=f"Keep the code `{datapoint}`? (Y/N): ", response_type="boolean")
                    if keep_code:  # add new code to res_detail_codes without changing datapoint
                        descript = handle_input(f"What activity does `{datapoint}` stand for?: ")
                        detail_codes[datapoint] = descript
                    else:  # add new code to res_detail_codes and change datapoint
                        code = handle_input(f"Enter a 1-char code to replace `{datapoint}`: ").upper()
                        if code not in detail_codes:
                            descript = handle_input(f"What activity does `{code}` stand for?: ")
                            detail_codes[code] = descript
                        code_translator[datapoint] = code
                        datapoint = code
        date = df["date"][curr_day]
        app_data[res_id]["data"][date] = datapoint
        curr_day += 1
    curr_day = 0
    curr_col += 1

print("*** Making backup copy of current resolutions data before save")
ts = int(datetime.now().timestamp())
shutil.copy("../data/resolutions.json", f"../data/backups/resolutions_{ts}.json")
print("*** Saving backpopulated resolutions data")
with open("../data/resolutions.json", "w+") as f:
    json.dump(app_data, f, indent=4)
print("*** Saved!")
