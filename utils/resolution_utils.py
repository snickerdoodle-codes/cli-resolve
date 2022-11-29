import json


def get_all_resolutions():
    with open("../data/resolutions.json", "r") as f:
        all_res_dict = json.load(f)
    return all_res_dict


def get_active_resolutions():
    with open("../data/resolutions.json", "r") as f:
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