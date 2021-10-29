from BiblioAlly import gui
from BiblioAlly import catalog as cat


def main():
    base_path = "..\\"
    base_file = base_path + 'DeceptionDetection.db'
    #base_path = ".\\tests\\"
    #base_file = base_path + 'BiblioAllyTests.db'
    catalog = cat.Catalog(base_file)

    browser = gui.Browser(catalog)
    browser.show()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
