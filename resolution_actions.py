from datetime import date

from resolution_utils import *
from menu_utils import *


def log_resolutions():
    active_res = get_active_resolutions()
    if not active_res:
        print("You don't have any active resolutions!")
        go_home()
        return
    today_or_backdate = input("Are you logging for today? ('Y' or 'MM/DD/YYYY' for backdate): ").upper()
    if today_or_backdate == "Y":
        log_date = date.today().strftime("%m/%d/%Y")
    else:
        # TODO: validate input
        log_date = today_or_backdate
    for res, val in active_res.items():
        if val['is_binary']:
            response = input(f"- Did you `{val['res_descript']}`? (Y/N): ").upper()
            if response == "Y":
                val['data'][log_date] = True
            elif response == "N":
                val['data'][log_date] = False
            else:
                print(f"Invalid input: {response}")
        else:
            print(f"- Did you `{val['res_descript']}`?")
            codes = val["res_detail_codes"]
            print_detail_codes(codes)
            # TODO: validate input
            response = input(f"Enter an existing or new detail code, a comma-separated list of existing detail codes,"
                             f" or 'N' for no: ").upper()
            if response == "N":
                val['data'][log_date] = False
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
                val['data'][log_date] = response
    # TODO: preview new log
    # Persist to file
    print("*** Saving new logs")
    with open("data/resolutions.json", "r") as f:
        all_res_dict = json.load(f)
        all_res_dict.update(active_res)
    with open("data/resolutions.json", "w") as f:
        json.dump(all_res_dict, f, indent=4)
    print(f"*** Saved logs for {log_date}!")
    go_home()


def add_resolution():
    while True:
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

        print(f"Preview: {res_dict}")
        confirm = input("Does everything look right? (Y/N): ").upper()
        if confirm == "Y":
            print("*** Adding new resolution")
            with open("data/resolutions.json", "r") as f:
                all_res_dict = json.load(f)
                all_res_dict.update(res_dict)
            with open("data/resolutions.json", "w") as f:
                json.dump(all_res_dict, f, indent=4)
            print("*** Added new resolution!")
            go_home()
            return
        else:
            print("Let's try this again")


def toggle_active_resolutions():
    all_res_dict = get_all_resolutions()

    if len(all_res_dict) == 0:
        print("No resolutions found")
        go_home()

    while True:
        print("Printing resolutions and is_active status:")
        for key, val in all_res_dict.items():
            print(f"* {key}: {val['is_active']}")
        res_key = input("Which resolution would you like to toggle?: ")
        if res_key == "m":
            return
        try:
            all_res_dict[res_key]["is_active"] = not all_res_dict[res_key]["is_active"]
            with open("data/resolutions.json", "w") as f:
                json.dump(all_res_dict, f, indent=4)
            print(f"*** Toggled active status of `{res_key}`!")

        except KeyError as e:
            print(f"No such resolution key={e}")
