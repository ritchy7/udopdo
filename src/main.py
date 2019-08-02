from math import ceil
from mysql.connector import (
    connect,
)
import requests
from constant import MESSAGE_PROMPT


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


def update_database():
    """
    Update the database.
    """
    # Get all categories.
    response = requests.get('https://fr.openfoodfacts.org/categories.json').json()
    for category in response['tags']:
        url = category['url']
        total_page = ceil(category['products'] / 20)
        counter = 1
        while counter < total_page:
            response = requests.get(f'{url}/{counter}.json').json()
            for p in response['products']:
                product = {
                    'product_id' : p['id'],
                    'product_name':  p['product_name'] if 'product_name' in p else None,
                    'img_url': p['image_url'] if 'image_url' in p else None,
                    'salt': p['nutrient_levels']['salt'] if 'salt' in p['nutrient_levels'] else None,
                    'fat': p['nutrient_levels']['fat'] if 'fat' in p['nutrient_levels'] else None,
                    'sugars': p['nutrient_levels']['sugars'] if 'sugars' in p['nutrient_levels'] else None,
                    'saturated_fat': p['nutrient_levels']['saturated-fat'] if 'saturated-fat' in p else None,
                    'warehouse': p['brands'] if 'brands' in p else None,
                    'allergens': p['allergens'] if 'allergens' in p else None,
                    'categories': p['categories'] if 'categories' in p else None
                }
                print(product)
                break
            break
            counter += 1            
        break


def ask_choice(message):
    """
    Ask for choice in the main menu.

    :param message:             Prompt message.
    :return choice (string):    Input choice.
    """
    while True:
        choice = input(message)
        if choice != '1' and choice != '2' and choice != '3':
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
        update_database()
    else:
        print('ERROR DURING CHOICE')
        exit()

