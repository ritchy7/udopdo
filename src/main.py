from math import ceil
from mysql.connector import connect
import requests
from constant import (
    CINFO,
    MESSAGE_PROMPT
)


def select_category():
    """
    Select a category.
    """
    print('Select the category')


def select_food():
    """
    Select a food.
    """
    print('Select the food')


def update_database(cinfo):
    """
    Update the database.

    :param cinfo (dict):    Connection informations.
    """
    # Init the connection with the database.
    try:
        openfoodfact_db = connect(**cinfo)
        cursor = openfoodfact_db.cursor()
        categories_query = 'INSERT INTO Category (category_name) VALUES (%s);'
        products_query = """
            INSERT INTO Product (product_name, img_url, salt, fat,
            sugars, saturated_fat, warehouse, allergens, category)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
    except Exception as err:
        print(f'Error during the connection:\n{err}\nexit\n')
        exit()
    response = requests.get('https://fr.openfoodfacts.org/categories.json').json()
    # Browse all categories.
    print('Database sync started.')
    for category in response['tags']:
        category_name = category['name']
        total_page = ceil(category['products'] / 20)
        url = category['url']
        if total_page > 10:
            total_page = 10
        page = 1
        products = []
        # Insert category into the database.
        cursor.execute(categories_query, (category_name,))
        category_id = cursor.lastrowid
        # Browse all pages of a category.
        print(f"Category {category['name']} sync in progress..")
        while page <= total_page:
            print(f'Page : {page}')
            response = requests.get(f'{url}/{page}.json').json()
            # Add all products into a huge list.
            for p in response['products']:
                products.append([
                    p['product_name'] if 'product_name' in p else None,
                    p['image_url'] if 'image_url' in p else None,
                    p['nutrient_levels']['salt'] if 'salt' in\
                        p['nutrient_levels'] else None,
                    p['nutrient_levels']['fat'] if 'fat' in\
                         p['nutrient_levels'] else None,
                    p['nutrient_levels']['sugars'] if 'sugars' in\
                        p['nutrient_levels'] else None,
                    p['nutrient_levels']['saturated-fat'] if 'saturated-fat'\
                        in p else None,
                    p['brands'] if 'brands' in p else None,
                    p['allergens'] if 'allergens' in p else None,
                    category_id
                ])
            # Insert all the products for a category.
            try:
                cursor.executemany(query, products)
                openfoodfact_db.commit()
            except Exception as e:
                print('error:', e)
                exit()
            page += 1
        break
    cursor.close()
    openfoodfact_db.close()


def ask_choice(message):
    """
    Ask for choice in the main menu.

    :param message:             Prompt message.
    :return choice (string):    Input choice.
    """
    while True:
        choice = input(message)
        if choice != '1' and choice != '2' and choice != '3' and choice != 'q':
            print(f'\'{choice}\' n\'est pas valide.\n')
        else:
            return choice


if __name__ == '__main__':
    choice = ask_choice(MESSAGE_PROMPT)
    if choice == '1':
        select_category()
    elif choice == '2':
        select_food()
    elif choice == '3':
        update_database(CINFO)
    elif choice == 'q':
        print('\nYou\'ve choice to exit the program\nExit\n')
    else:
        print('ERROR DURING CHOICE')
        exit()

