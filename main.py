from menu import Menu


def visualize_resolutions():
    pass


# TODO: users should be able to return to main menu at any time by entering 'm'
# this should abort their current operation if they're trying to add or edit something
def main():
    while True:
        menu = Menu()
        menu.print_menu()


if __name__ == "__main__":
    main()
