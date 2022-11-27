import sys
from time import sleep

from resolution_actions import *
from export_actions import *


class Menu:
    def __init__(self):
        self.options = {
            "1": {
                "text": "log resolutions",
                "function": log_resolutions,
            },
            "2": {
                "text": "add resolution",
                "function": add_resolution,
            },
            "3": {
                "text": "toggle active resolutions",
                "function": toggle_active_resolutions,
            },
            "4": {
                "text": "export csv",
                "function": export_csv,
            },
            "5": {
                "text": "export graph",
                "function": export_graph,
            }
        }

    def print_menu(self):
        os.system('clear')
        print(f"Welcome to ✨ Resolve ✨\n")
        for key, val in self.options.items():
            print(f"{key} - {val['text']}")
        print("Enter 'q' to quit\n")
        command = input("What would you like to do? (enter #): ")
        print()
        if command == "q":
            sys.exit("Goodbye!")
        try:
            self.options[command]["function"]()
        except KeyError as e:
            print(f"{command} is not a valid command")
            sleep(1)
