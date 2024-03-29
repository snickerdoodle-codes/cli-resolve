import json
from datetime import datetime


def add_detail_code(char):
    """
    Return dict for a new detail code where the key is the code and the value is that code's description.
    """
    print(f"`{char}` is not defined yet, but we can add it now")
    new_code_descript = input(f"What activity does `{char}` stand for?: ")
    return {char: new_code_descript}


def get_all_resolutions():
    """
    Returns dict of all resolutions.
    """
    with open("data/resolutions.json", "r") as f:
        all_res_dict = json.load(f)
    return all_res_dict


def get_active_resolutions():
    """
    Returns a dict with all currently active resolutions.
    Automatically inactivates resolutions past their expiration date.
    """
    with open("data/resolutions.json", "r") as f:
        all_res_dict = json.load(f)
    active_res_dict = {}
    for key, val in all_res_dict.items():
        if val["is_active"]:
            # Check against expiration date first and update active status if expired
            expiry = val["res_expiration_date"]
            if not expiry or datetime.strptime(expiry, "%m/%d/%Y") > datetime.today():
                active_res_dict[key] = val
            else:
                val["is_active"] = False
                with open("data/resolutions.json", "w") as f:
                    json.dump(all_res_dict, f, indent=4)
    return active_res_dict


def print_detail_codes(detail_codes):
    """
    Print a list of detail codes and descriptions.
    """
    codes = ""
    if detail_codes:
        for key, val in detail_codes.items():
            codes += f"{key} - {val}\n"
    return print(f"Existing codes:\n{codes}")


def print_resolutions_and_status(resolutions):
    """
    Prints all resolutions and whether currently active.
    """
    print("Printing resolutions and is_active status:")
    for key, val in resolutions.items():
        print(f"* {key}: {val['is_active']}")
    print()
