# Local libraries.
from classes import OpenFoodFacts
from constant import CINFO

if __name__ == '__main__':
    # Init the object.
    openfoodfacts = OpenFoodFacts(CINFO)
    # Init the connection.
    openfoodfacts.init_connection()
    while True:
        # Ask for a choice.
        openfoodfacts.main_selection_menu()
        main_menu_choice = openfoodfacts.main_menu_choice
        if main_menu_choice == 1:
            openfoodfacts.category_selection_menu()
        elif main_menu_choice == 2:
            openfoodfacts.show_saved_products()
        elif main_menu_choice == 3:
            openfoodfacts.update_database()
