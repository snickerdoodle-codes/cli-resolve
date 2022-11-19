from datetime import date
import json


def view_active_resolutions():
    pass


def add_resolution(curr_date):
    res_id = input("Enter a short ID for this resolution in snake_case: ")
    res_descript = input("Describe this resolution: ")
    res_creation_date = curr_date
    is_active = True
    is_nyres = input("Is this a New Year's resolution? (Y/N): ")
    # TODO: wrap converting Y/N inputs to True/False into a function
    if is_nyres.upper() == "Y":
        res_expiration_date = date(curr_date.year, 12, 31)
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


def update_todays_resolutions():
    pass


def visualize_resolutions():
    pass


def main():
    today = date.today()
    print(f"Welcome to ✨ Resolve ✨\nToday is {today}")
    command = input("What would you like to do?: ")
    if "add res" in command:
        add_resolution(today)


if __name__ == "__main__":
    main()
