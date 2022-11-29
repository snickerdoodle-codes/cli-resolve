import json


def booleanize_yes_no(input_str):
    """
    Takes the response to a Y/N question and outputs the corresponding boolean value.
    For invalid values, the input string is returned along with a flag indicating invalidity.
    :param input_str:
    :return:
    """
    if input_str.upper() == "Y":
        booleanized = True
        is_valid = True
    elif input_str.upper() == "N":
        booleanized = False
        is_valid = True
    else:
        booleanized = input_str
        is_valid = False
    return booleanized, is_valid


def get_all_resolutions():
    with open("../../data/resolutions.json", "r") as f:
        all_res_dict = json.load(f)
    return all_res_dict


def get_active_resolutions():
    with open("../../data/resolutions.json", "r") as f:
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
    return print(codes)
