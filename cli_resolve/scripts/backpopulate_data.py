import pandas as pd
import os
import sys
import json
from datetime import datetime

from ..utils.resolution_utils import *

# INPUTS
filename = "nyr19.csv"

# Read the CSV
filepath = f"../data/cleaned/{filename}"
if not os.path.exists(filepath):
    sys.exit(f"filepath={filepath} does not exist")

df = pd.read_csv(filepath)
pd.set_option('display.max_columns', None)
print(f"Preview of uploaded dataset:\n{df.head()}\n")

data_start = int(input("index of first column containing resolution data: "))
data_end = int(input("index of last column containing resolution data: "))

# Load app data
with open("data/back.json", "r") as f:
    app_data = json.load(f)

# Loop through each resolution column
days = len(df)
curr_day = 0
curr_col = data_start

while curr_col <= data_end:
    col_name = df.iloc[:, curr_col].name
    print(f"*** Adding data from resolution={col_name}")

    # Check whether this resolution already exists in app data
    exists = col_name in app_data
    first_date = df.iloc[0, 0]
    last_date = df.iloc[days - 1, 0]

    if exists:
        merge_data, is_valid = booleanize_yes_no(
            input(f"res={col_name} already exists. Merge with existing data? (Y/N): ")
        )
        if not is_valid:
            # TODO: handle invalid response
            print(f"Invalid input: {merge_data}")
        else:
            if merge_data:
                print(f"*** Merging res={col_name}")
                res_id = col_name

                # Calculate res_creation_date (first date entry from current data OR res_creation_date of existing
                # resolution, whichever is earlier)
                first_date_dt = datetime.strptime(first_date, "%m/%d/%Y")
                exist_creation_date = app_data[col_name]["res_creation_date"]
                exist_creation_date_dt = datetime.strptime(exist_creation_date, "%m/%d/%Y")
                res_creation_date = first_date if first_date_dt < exist_creation_date_dt else exist_creation_date

                # Expiration is last date entry from current data OR res_expiration_date of existing resolution,
                # whichever is later
                last_date_dt = datetime.strptime(last_date, "%m/%d/%Y")
                exist_expiration_date = app_data[col_name]["res_expiration_date"]
                exist_expiration_date_dt = datetime.strptime(exist_expiration_date, "%m/%d/%Y")
                res_expiration_date = last_date if last_date_dt > exist_expiration_date_dt else exist_expiration_date_dt

                # TODO: extract res_detail_codes
                res_detail_codes = {}

                app_data[res_id].update(
                    {
                        "res_creation_date": res_creation_date,
                        "res_expiration_date": res_expiration_date,
                        "res_detail_codes": res_detail_codes,
                    }
                )
    # New resolution without precedent
    if (not exists) or (not merge_data):
        if exists:
            res_id = input(f"Let's give this resolution a new res_id to differentiate it from {col_name}: ")
        else:
            keep_name, is_valid = booleanize_yes_no(input(f"Want to keep the res_id `{col_name}`? (Y/N): "))
            if not is_valid:
                # TODO: handle invalid response
                print(f"Invalid input: {keep_name}")
            elif keep_name:
                res_id = col_name
            else:
                res_id = input("Let's give this resolution a new res_id: ")
        print(f"*** Creating a new resolution res={res_id}")
        res_descript = input("Provide a short description for this resolution: ")
        res_creation_date = df.iloc[0, 0]  # first date entry from current data
        is_active, is_valid = booleanize_yes_no(input("Is this an active resolution? (Y/N): "))
        if not is_valid:
            # TODO: handle invalid input
            pass
        is_expired = booleanize_yes_no(input(f"Did this resolution expire on {last_date}? (Y/N)"))
        if is_expired:
            res_expiration_date = last_date
        else:
            res_expiration_date = input(
                "When does this resolution expire? ('MM/DD/YYYY' or 'N' for no expiration): ").upper()
            if res_expiration_date == "N":
                res_expiration_date = None
            # TODO: validate and clean input

        is_binary, is_valid = booleanize_yes_no(
            input("Is this resolution's outcome binary? For example, for the resolution to exercise, "
                  "a binary outcome is whether you exercised or did not exercise. "
                  "In contrast, a categorical outcome names the kind of exercise you did (e.g. "
                  "run/bike/swim). (Y/N): ")
        )
        if not is_valid:
            # TODO: handle invalid response
            print(f"Invalid input: {merge_data}")

        # TODO: extract res_detail_codes
        res_detail_codes = {}

        res = {
            "res_descript": res_descript,
            "res_creation_date": res_creation_date,
            "is_active": is_active,
            "res_expiration_date": res_expiration_date,
            "is_binary": is_binary,
            "res_detail_codes": res_detail_codes,
            "data": {},
        }
        app_data[res_id].update(res)

    # Populate the data dict for both merged and new resolutions
    print("*** Backpopulating resolutions data")
    while curr_day < days:
        datapoint = df.iloc[curr_day, curr_col]
        date = df.iloc[curr_day, 0]
        app_data[res_id]["data"][date] = datapoint
        curr_day += 1
    curr_day = 0
    curr_col += 1

print("*** Saving backpopulated resolutions data")
with open("../../data/back.json", "w+") as f:
    json.dump(app_data, f, indent=4)
print("*** Saved!")
