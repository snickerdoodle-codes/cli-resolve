import pandas as pd
import os
import sys
import json

# INPUTS
filename = "nyr19.csv"

# Read the CSV
filepath = f"../data/converted/{filename}"
if not os.path.exists(filepath):
    sys.exit(f"filepath={filepath} does not exist")

df = pd.read_csv(filepath)
pd.set_option('display.max_columns', None)
print(f"Preview of uploaded dataset:\n{df.head()}\n")

data_start = int(input("index of first column containing resolution data: "))
data_end = int(input("index of last column containing resolution data: "))

# Loop through each resolution column
days = len(df)
curr_day = 0
curr_col = data_start
resolutions = {}
while curr_col <= data_end:
    col_name = df.iloc[:, curr_col].name
    print(f"Adding resolution={col_name}")
    # TODO: option to enter a different res_id
    # TODO: check whether this resolution already exists in app data
    # TODO: DRY these prompts here and in resolutions.py
    res_descript = input("Provide a short description for this resolution: ")
    # TODO: calculate res_creation_date (first date entry from current data OR res_creation_date of existing
    #  resolution, whichever is earlier)
    res_creation_date = ""
    is_active = input("Is this an active resolution? (Y/N): ").upper()
    if is_active == "Y":
        is_active = True
    elif is_active == "N":
        is_active = False
    else:
        # TODO: handle invalid input
        pass
    # TODO: Expiration is last date entry from current data OR res_expiration_date of existing resolution,
    #  whichever is later
    res_expiration_date = input("When does this resolution expire? ('MM/DD/YYYY' or 'N' for no expiration): ").upper()
    if res_expiration_date == "N":
        res_expiration_date = None
    else:
        # TODO: validate and clean input
        pass
    is_binary = input("Is this resolution's outcome binary? For example, for the resolution to exercise, "
                      "a binary outcome is whether you exercised or did not exercise. "
                      "In contrast, a categorical outcome names the kind of exercise you did (e.g. "
                      "run/bike/swim). (Y/N): ").upper()
    if is_binary == "Y":
        is_binary = True
    elif is_binary == "N":
        is_binary = False
    else:
        # TODO: Invalid input
        pass
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
    resolutions[col_name] = res
    while curr_day < days - 1:
        datapoint = df.iloc[curr_day, curr_col]
        date = df.iloc[curr_day, 0]
        res["data"][date] = datapoint
        curr_day += 1
    curr_day = 0
    curr_col += 1

print("*** Backpopulating resolutions data")
with open("../data/back.json", "w+") as f:
    json.dump(resolutions, f, indent=4)
print("*** Saved!")
