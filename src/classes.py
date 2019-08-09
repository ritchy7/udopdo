from constant import MESSAGE_PROMPT
from math import ceil
from mysql.connector import connect
import requests


class OpenFoodFacts:

    def __init__(self, ):
        self.category_id = None
        self.choice = None
        self.cursor = None
        self.database = None

    def ask_choice(self):
        """
        Ask for choice in the main menu.
        """
        choice = None

        while True:
            choice = input(MESSAGE_PROMPT)

            if choice == '1':
                self.choice = 1
                break
            elif choice == '2':
                self.choice = 2
                break
            elif choice == '3':
                self.choice = 3
                break
            elif choice == 'q':
                print('\nYou\'ve choice to exit the program\Bye bye\n')
                break
            else:
                print(f'\'{choice}\' n\'est pas valide.\n')

    def select_category(self):
        """
        Select a category.
        """
        print('Select the category')

    def select_food(self):
        """
        Select a food.
        """
        print('Select the food')

    def init_connection(self, cinfo):
        """
        Initalize the connection.

        :param cinfo (dict):   Connection informations.
        """
        # Init the connection with the database.
        try:
            self.database = connect(**cinfo)
            self.cursor = self.database.cursor()
        except Exception as err:
            print(f'Error during the connection:\n{err}\nexit\n')
            exit()

    def truncate_tables(self):
        """
        Truncate all tables.
        """
        try:
            drop_query = "DELETE FROM {};"
            tables = ['History', 'Product', 'Category']
            # Drop the tables.
            for table in tables:
                self.cursor.execute(drop_query.format(table))
                self.database.commit()
        except Exception as err:
            print(f'Error during droping tables:\n{err}\nexit\n')
            exit()

    def insert_products(self, product_number, url):
        """
        Insert all products off each category into the database.

        :param product_number:  Number of product.
        :param url:             Category url.
        """
        products_query = """
            INSERT INTO Product (product_name, img_url, salt, fat,
            sugars, saturated_fat, warehouse, allergens, category)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        total_page = ceil(product_number / 20)
        # Limit to 200 products per category.
        if total_page > 10:
            total_page = 10
        page = 1
        # Browse all pages of a category.
        while page <= total_page:
            print(f'Page : {page}')
            response = requests.get(f'{url}/{page}.json').json()
            # Add all products into a huge list.
            products = [
                (
                    p.get('product_name'),
                    p.get('image_url'),
                    p['nutrient_levels'].get('salt'),
                    p['nutrient_levels'].get('fat'),
                    p['nutrient_levels'].get('sugars'),
                    p['nutrient_levels'].get('saturated-fat'),
                    p.get('brands'),
                    p.get('allergens'),
                    self.category_id
                )
                for p in response['products']
            ]
            # Insert all the products for a category into 'Product' table.
            try:
                self.cursor.executemany(products_query, products)
                self.database.commit()
            except Exception as e:
                print('error:', e)
                exit()
            page += 1

    def insert_category(self, category_name):
        """
        Insert a category into the database.

        :param category_name:   category's name.
        """
        categories_query = 'INSERT INTO Category (category_name) VALUES (%s);'
        try:
            # Insert category into the database.
            self.cursor.execute(categories_query, (category_name,))
            self.category_id = self.cursor.lastrowid
            print(f"Category {category_name} sync in progress..")
        except Exception as err:
            print(f'Error during insertion (category):\n{err}\nexit\n')
            exit()

    def update_database(self):
        """
        Update the database.
        """
        response = requests.get('https://fr.openfoodfacts.org/categories.json').json()
        # Browse all categories.
        print('Database sync started..')
        print(100 * '=')
        for category_number, category in enumerate(response['tags']):
            self.insert_category(category['name'])
            self.insert_products(category['products'], category['url'])
            if category_number >= 20:
                break
            print(100 * '=')
        self.cursor.close()
        self.database.close()
        print("Database sync finished")
