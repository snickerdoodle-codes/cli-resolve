from utils.input_utils import *
from utils.resolution_utils import *
from utils.menu_utils import *


def log_resolutions():
    """
    Log entry for all active resolutions.
    :return:
    """
    active_res = get_active_resolutions()
    if not active_res:
        print("You don't have any active resolutions!")
        return go_home_message()

    log_date = handle_input(prompt="What is the date for this entry? ('today' or 'MM/DD/YYYY'): ",
                            response_type="datestring")
    for res, val in active_res.items():
        if val['is_binary']:
            prompt = f"- Did you `{val['res_descript']}`? (Y/N): "
            response = handle_input(prompt=prompt, response_type="boolean")
            val['data'][log_date] = response
        else:
            codes = val["res_detail_codes"]
            print(f"codes: {codes}")
            prompt = f"- Did you `{val['res_descript']}`? "
            instructions = "Enter an existing or new detail code, a comma-separated list of existing detail codes, " \
                           "or 'N' for no."
            response = handle_input(prompt=prompt, response_type="code", instructions=instructions, codes=codes)
            val['data'][log_date] = response

    # Persist to file
    print("*** Saving new logs")
    with open("data/resolutions.json", "r") as f:
        all_res_dict = json.load(f)
        all_res_dict.update(active_res)
    with open("data/resolutions.json", "w") as f:
        json.dump(all_res_dict, f, indent=4)
    print(f"*** Saved logs for {log_date}!")
    return go_home_message()


def add_resolution():
    all_res_dict = get_all_resolutions()
    while True:
        try:
            res_id = handle_input(prompt="Enter a short ID for this resolution in snake_case: ")
            if res_id in all_res_dict:
                print(f"`{res_id}` already exists")
                continue
            res_descript = handle_input(prompt="Describe this resolution: ")
            res_creation_date = date.today()
            is_active = True
            res_expiration_date = handle_input(
                prompt="When does this resolution expire? ('MM/DD/YYYY' or 'never' for no "
                "expiration): ",
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
            if not is_binary:
                print(
                    "You will be able to tell me what kind of activity you did when you log an entry for this "
                    "resolution."
                )
            res_detail_codes = {}
        except ValueError as e:
            print(f"Invalid input: {e}")
            continue

        res_dict = {
            res_id: {
                "res_descript": res_descript,
                "res_creation_date": res_creation_date.strftime("%-m/%-d/%Y"),
                "is_active": is_active,
                "res_expiration_date": res_expiration_date,
                "is_binary": is_binary,
                "res_detail_codes": res_detail_codes,
                "data": {},
            }
        }

        print(f"Preview: {res_dict}")
        confirm = handle_input(prompt="Does everything look right? (Y/N): ", response_type="boolean")
        if confirm:
            print(f"*** Adding new resolution={res_id}")
            all_res_dict.update(res_dict)
            with open("data/resolutions.json", "w+") as f:
                json.dump(all_res_dict, f, indent=4)
            print("*** Added new resolution!")
            return go_home_message()
        else:
            print("Okay, let's try this again.")
            continue


def toggle_active_resolutions():
    """
    Toggle the is_active status of resolutions.
    Resolutions are considered active if they are currently being tracked.
    :return:
    """
    all_res_dict = get_all_resolutions()

    if len(all_res_dict) == 0:
        print("No resolutions found")
        return go_home_message()

    while True:
        print_resolutions_and_status(all_res_dict)
        res_key = handle_input(prompt="Which resolution would you like to toggle?: ",
                               instructions="Enter 'menu' to go back")
        if res_key == "menu":
            break
        try:
            all_res_dict[res_key]["is_active"] = not all_res_dict[res_key]["is_active"]
            with open("data/resolutions.json", "w") as f:
                json.dump(all_res_dict, f, indent=4)
            print(f"*** Toggled active status of `{res_key}`!\n")
        except KeyError as e:
            print(f"No such resolution key={e}")
