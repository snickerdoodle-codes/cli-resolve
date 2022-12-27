import os
from time import sleep


def go_home_message(delay=2):
    """
    Takes the user back to the main menu after a small delay (for UX purposes)
    """
    if delay > 0:
        print("*** Taking you back to main menu in 3, 2, 1...")
    sleep(delay)
    os.system('clear')
