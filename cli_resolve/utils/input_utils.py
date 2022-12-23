import sys
from datetime import date, datetime

from .resolution_utils import print_detail_codes, add_detail_code


def get_index_response(prompt, num_cols):
    while True:
        command = input(prompt)
        try:
            value = int(command)
            if value < 0 or value > num_cols - 1:
                raise ValueError(f"Index {value} out of range for current dataset")
            else:
                return value
        except ValueError as value_e:
            print(f"Invalid input: {value_e}")
            continue


def get_date_string_response(prompt, year_start=False, year_end=False):
    """
    Generic function for handling prompts requiring date string user inputs
    :param prompt:
    :param year_end:
    :param year_start:
    :return:
    """
    while True:
        command = input(prompt)
        try:
            if command.lower() == "today":
                return date.today().strftime("%-m/%-d/%Y")
            if command.lower() == "never":
                return None
            if command.lower() == "file":
                return "file"
            if year_start:
                command = f"1/1/{command}"
            if year_end:
                command = f"12/31/{command}"
            validate_date_string(command)
            return command
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


def get_boolean_response(prompt):
    """
    Takes the response to a Y/N question and outputs the corresponding boolean value if input is valid.
    :param prompt:
    :return:
    """
    while True:
        command = input(prompt)
        try:
            if command.upper() == "Y":
                return True
            elif command.upper() == "N":
                return False
            else:
                raise ValueError("Input should be 'Y' or 'N'")
        except ValueError as e:
            print(f"Invalid input: {e}")
            continue


def get_detail_code_response(prompt, existing_codes):
    while True:
        command = input(prompt)
        try:
            print_detail_codes(existing_codes)

            if command.upper() == "N":
                return False

            code_list = command.split(",")
            # Check that each code is already a defined code, or add it now
            for char in code_list:
                code = char.upper()
                if len(char) > 1:
                    raise ValueError(f"Code should be of len=1; found len={len(char)} for code `{char}`")
                if code not in existing_codes:
                    existing_codes.update(add_detail_code(code))
            return command
        except ValueError as e:
            print(f"Invalid input: {e}")
            continue


def handle_input(prompt, response_type=None, **kwargs):
    # Print instructions first if provided
    if kwargs.get("instructions"):
        print(f"INSTRUCTIONS: {kwargs['instructions']}\n")

    # Without a specified response type, we just want the input string, no validation required
    if not response_type:
        command = input(prompt)
        if command == "q":
            sys.exit("Goodbye!")
        return command
    elif response_type == "index":
        return get_index_response(prompt, num_cols=kwargs["num_cols"])
    elif response_type == "datestring":
        return get_date_string_response(
            prompt,
            year_start=kwargs.get("year_start", False),
            year_end=kwargs.get("year_end", False)
        )
    elif response_type == "boolean":
        return get_boolean_response(prompt)
    elif response_type == "code":
        return get_detail_code_response(
            prompt,
            existing_codes=kwargs.get("codes")
        )
    else:
        return print(f"Something went wrong: we don't know how to handle command={command} "
                     f"with response_type={response_type}")
