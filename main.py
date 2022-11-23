import os
import sys
from datetime import date
import json
from time import sleep
import csv
from utils import *


def get_active_resolutions():
    with open("sample.json", "r") as f:
        all_res_dict = json.load(f)
    active_res_dict = {}
    for key, val in all_res_dict.items():
        if val["is_active"]:
            active_res_dict[key] = val
    return active_res_dict


def add_resolution():
    today = date.today()
    res_id = input("Enter a short ID for this resolution in snake_case: ")
    # TODO: check that res_id has not already been used
    res_descript = input("Describe this resolution: ")
    res_creation_date = today
    is_active = True
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
    if not is_binary:
        print("You will be able to tell me what kind of activity you did when you log an entry for this resolution.")
    res_detail_codes = {}

    res_dict = {
        res_id: {
            "res_descript": res_descript,
            "res_creation_date": res_creation_date.strftime("%m/%d/%Y"),
            "is_active": is_active,
            "res_expiration_date": res_expiration_date,
            "is_binary": is_binary,
            "res_detail_codes": res_detail_codes,
            "data": {},
        }
    }

    print("*** Adding new resolution")
    with open("sample.json", "r") as f:
        all_res_dict = json.load(f)
        all_res_dict.update(res_dict)
    with open("sample.json", "w") as f:
        json.dump(all_res_dict, f, indent=4)
    print("*** Added new resolution!")
    go_home()


def edit_resolution():
    pass


def deactivate_resolution():
    pass


def print_detail_codes(detail_codes):
    codes = ""
    if detail_codes:
        for key, val in detail_codes.items():
            codes += f"{key} - {val}\n"
    return print(codes)


def log_resolutions():
    active_res = get_active_resolutions()
    if not active_res:
        go_home()
        return
    today = date.today().strftime("%m/%d/%Y")
    for res, val in active_res.items():
        if val['is_binary']:
            response = input(f"- Did you `{val['res_descript']}` today? (Y/N): ").upper()
            if response == "Y":
                val['data'][today] = True
            elif response == "N":
                val['data'][today] = False
            else:
                print(f"Invalid input: {response}")
        else:
            print(f"- Did you `{val['res_descript']}` today?")
            codes = val["res_detail_codes"]
            print_detail_codes(codes)
            # TODO: validate input
            response = input(f"Enter an existing or new detail code, a comma-separated list of existing detail codes,"
                             f" or 'N' for no: ").upper()
            if response == "N":
                val['data'][today] = False
            # Split response into list
            else:
                response_list = response.split(",")
                # Check that each code is already a defined code
                for char in response_list:
                    if char not in codes:
                        print(f"`{char}` is not defined yet, but we can add it now")
                        new_code_descript = input(f"What activity does `{char}` stand for?: ")
                        new_code = {char: new_code_descript}
                        codes.update(new_code)
                val['data'][today] = response
    # Persist to file
    print("*** Saving new logs")
    with open("sample.json", "r") as f:
        all_res_dict = json.load(f)
        all_res_dict.update(active_res)
    with open("sample.json", "w") as f:
        json.dump(all_res_dict, f, indent=4)
    print(f"*** Saved logs for {today}!")
    go_home()


def visualize_resolutions():
    pass


OPTION_MENU = {
    "1": {
        "text": "log resolutions",
        "function": log_resolutions,
    },
    "2": {
        "text": "add resolution",
        "function": add_resolution,
    },
    "3": {
        "text": "view active resolutions",
        "function": get_active_resolutions,
    },
}


# TODO: users should be able to return to main menu at any time by entering 'main'
def main():
    while True:
        print(f"Welcome to ✨ Resolve ✨\n")
        for key, val in OPTION_MENU.items():
            print(f"{key} - {val['text']}")
        print("Enter 'q' to quit\n")
        command = input("What would you like to do? (enter #): ")
        if command == "q":
            sys.exit("Goodbye!")
        OPTION_MENU[command]["function"]()


if __name__ == "__main__":
    main()
