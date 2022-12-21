import os
import sys
from time import sleep


def go_home_message(delay=2):
    """
    Takes the user back to the main menu after a showy message
    :return:
    """
    if delay > 0:
        print("*** Taking you back to main menu in 3, 2, 1...")
    sleep(delay)
    os.system('clear')


def goto_menu():
    return go_home_message()


# TODO: use this function to handle all inputs by redirecting inputs to the appropriate response getter function
#  (e.g. get_boolean_response); eventually move functions to an input_utils.py
def handle_input(prompt):
    command = input(prompt)
    if command == "q":
        sys.exit("Goodbye!")
    if command == "menu":
        goto_menu()
    else:
        return command
