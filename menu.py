import sys
import os

from resolution_actions import *


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
        }

    def print_menu(self):
        os.system('clear')
        print(f"Welcome to ✨ Resolve ✨\n")
        for key, val in self.options.items():
            print(f"{key} - {val['text']}")
        print("Enter 'q' to quit\n")
        command = input("What would you like to do? (enter #): ")
        if command == "q":
            sys.exit("Goodbye!")
        self.options[command]["function"]()
