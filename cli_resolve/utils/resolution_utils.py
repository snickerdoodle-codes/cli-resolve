from datetime import datetime, date
import json


def get_date_string_response(prompt, instructions=None, year_start=False, year_end=False):
    """
    Generic function for handling prompts requiring date string user inputs
    :param prompt:
    :param instructions:
    :param year_end:
    :param year_start:
    :return:
    """
    while True:
        try:
            if instructions:
                print(f"INSTRUCTIONS: {instructions}\n")
            value = input(prompt)
            if year_start:
                value = f"1/1/{value}"
            if year_end:
                value = f"12/31/{value}"
            if value.lower() == "today":
                return date.today().strftime("%-m/%-d/%Y")
            elif value.lower() == "never":
                return None
            else:
                validate_date_string(value)
                return value
        except ValueError as e:
            print(f"Invalid input: {e}")
            continue


def validate_date_string(date_string):
    """
    Validates date input strings to ensure that they are in 'MM/DD/YYYY' format
    :param date_string:
    :return:
    """
    try:
        datetime.strptime(date_string, "%m/%d/%Y")
    except ValueError:
        raise ValueError(f"Invalid date={date_string}; date input should be in the form of 'MM/DD/YYYY'")


def get_boolean_response(prompt, instructions=None):
    """
    Takes the response to a Y/N question and outputs the corresponding boolean value if input is valid.
    :param prompt:
    :param instructions:
    :return:
    """
    while True:
        try:
            if instructions:
                print(f"INSTRUCTIONS: {instructions}\n")
            value = input(prompt)
            if value.upper() == "Y":
                return True
            elif value.upper() == "N":
                return False
            else:
                raise ValueError("Input should be 'Y' or 'N'")
        except ValueError as e:
            print(f"Invalid input: {e}")
            continue


def get_detail_code_response(prompt, instructions, existing_codes):
    while True:
        try:
            print(f"INSTRUCTIONS: {instructions}\n")
            print_detail_codes(existing_codes)
            value = input(prompt)

            if value.upper() == "N":
                return False

            code_list = value.split(",")
            # Check that each code is already a defined code, or add it now
            for char in code_list:
                code = char.upper()
                if len(char) > 1:
                    raise ValueError(f"Code should be of len=1; found len={len(char)} for code `{char}`")
                if code not in existing_codes:
                    existing_codes.update(add_detail_code(code))
            return value
        except ValueError as e:
            print(f"Invalid input: {e}")
            continue


def add_detail_code(char):
    print(f"`{char}` is not defined yet, but we can add it now")
    new_code_descript = input(f"What activity does `{char}` stand for?: ")
    return {char: new_code_descript}


def get_all_resolutions():
    with open("data/back.json", "r") as f:
        all_res_dict = json.load(f)
    return all_res_dict


def get_active_resolutions():
    with open("data/resolutions.json", "r") as f:
        all_res_dict = json.load(f)
    active_res_dict = {}
    for key, val in all_res_dict.items():
        if val["is_active"]:
            active_res_dict[key] = val
    return active_res_dict


def print_detail_codes(detail_codes):
    codes = ""
    if detail_codes:
        for key, val in detail_codes.items():
            codes += f"{key} - {val}\n"
    return print(f"Existing codes:\n{codes}")


def print_resolutions_and_status(resolutions):
    print("Printing resolutions and is_active status:")
    for key, val in resolutions.items():
        print(f"* {key}: {val['is_active']}")