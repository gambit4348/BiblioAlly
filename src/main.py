import gui
from catalog import Catalog

# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def main():
    base_path = "..\\"
    base_file = base_path + "DeceptionDetection.db"
    catalog = Catalog(base_file)

    browser = gui.Browser(catalog)
    browser.show()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
