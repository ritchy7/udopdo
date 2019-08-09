from classes import OpenFoodFacts
from constant import CINFO

if __name__ == '__main__':
    # Init the object.
    openfoodfacts = OpenFoodFacts()
    # Init the connection.
    openfoodfacts.init_connection(CINFO)
    # Ask for a choice.
    openfoodfacts.ask_choice()
    choice = openfoodfacts.choice
    if choice == 1:
        openfoodfacts.select_category()
    elif choice == 2:
        pass
    elif choice == 3:
        openfoodfacts.update_database()
