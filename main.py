from datetime import date
import json
from utils import *


def view_active_resolutions():
    pass


def add_resolution():
    today = date.today()
    res_id = input("Enter a short ID for this resolution in snake_case: ")
    res_descript = input("Describe this resolution: ")
    res_creation_date = today
    is_active = True
    is_nyres = input("Is this a New Year's resolution? (Y/N): ")
    # TODO: wrap converting Y/N inputs to True/False into a function
    if is_nyres.upper() == "Y":
        res_expiration_date = date(today.year, 12, 31)
    elif is_nyres.upper() == "N":
        # Does this resolution have an expiration date?
        pass
    else:
        # Invalid input
        pass
    is_binary = input("Is this resolution's outcome binary? For example, for the resolution to exercise, "
                            "a binary outcome is whether you exercised or did not exercise. "
                            "In contrast, a categorical outcome names the kind of exercise you did (e.g. "
                            "run/bike/swim). (Y/N): ")
    if is_binary.upper() == "Y":
        is_binary = True
    elif is_binary.upper() == "N":
        is_binary = False
    else:
        # Invalid input
        pass
    if not is_binary:
        res_detail_codes = {}

    res_dict = {
        res_id: {
            "res_descript": res_descript,
            "res_creation_date": res_creation_date.strftime("%m-%d-%Y"),
            "is_active": is_active,
            "res_expiration_date": res_expiration_date.strftime("%m-%d-%Y"),
            "is_binary": is_binary,
        }
    }

    with open("sample.json", "r") as f:
        all_res_dict = json.load(f)
        all_res_dict.update(res_dict)
    with open("sample.json", "w") as f:
        json.dump(all_res_dict, f)


def deactivate_resolution():
    pass


def log_resolutions():
    pass


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
}


def main():
    print(f"Welcome to ✨ Resolve ✨\n")
    for key, val in OPTION_MENU.items():
        print(f"{key} - {val['text']}")
    command = input("\nWhat would you like to do?: ")
    OPTION_MENU[command]["function"]()


if __name__ == "__main__":
    main()
