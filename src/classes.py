from constant import MESSAGE_PROMPT
from math import ceil
from mysql.connector import connect
import requests
import sys


class OpenFoodFacts:

    def __init__(self, cinfo):
        self.category_id = None
        self.main_menu_choice = None
        self.cinfo = cinfo
        self.cursor = None
        self.database = None

    def main_selection_menu(self):
        """
        Main selection menu.
        """
        main_menu_choice = None
        while True:
            main_menu_choice = input(MESSAGE_PROMPT)
            if main_menu_choice == '1':
                self.main_menu_choice = 1
                break
            elif main_menu_choice == '2':
                self.main_menu_choice = 2
                break
            elif main_menu_choice == '3':
                self.main_menu_choice = 3
                break
            elif main_menu_choice == 'q':
                print('\nYou\'ve decided to leave\nBye bye\n')
                break
            else:
                print(f'\'{main_menu_choice}\' n\'est pas valide.\n')

    def category_selection_menu(self):
        """
        Select a category.
        """
        self.cursor.execute('SELECT * FROM Category;')
        categories = '\n'.join([
            f'{k} - {v}' for k, v in dict(self.cursor.fetchall()).items()
        ])
        menu_message = f'Select a category :\n{categories}\n\nq - Quitter.\n\n'
        category_query = 'SELECT * FROM Product WHERE category = {};'
        while True:
            print(50 * '-')
            menu_choice = input(menu_message)
            if menu_choice == 'q':
                print('\nYou\'ve decided to leave\nBye bye\n')
                break
            elif menu_choice not in categories:
                print(f'category number {menu_choice} is not valid')
            else:
                try:
                    self.cursor.execute(category_query.format(menu_choice))
                    products = self.cursor.fetchall()
                    self.cursor.close()
                    self.database.commit()
                    self.product_selection_menu(products)
                except Exception as e:
                    print(f'Error during category selection: {e}')
                self.init_connection()

    def product_selection_menu(self, products):
        """
        Select a product.

        :param products (list):    Product list.
        """
        print(len(products))

    def init_connection(self):
        """
        Initalize the connection.
        """
        # Init the connection with the database.
        try:
            self.database = connect(**self.cinfo)
            self.cursor = self.database.cursor(buffered=True)
        except Exception as err:
            print(f'Error during the connection:\n{err}\nexit\n')
            sys.exit(1)

    def drop_tables(self):
        """
        drop all tables.
        """
        try:
            drop_query = "DELETE FROM {0};"
            reset_auto_increment = 'ALTER TABLE {0} AUTO_INCREMENT = 1;'
            tables = ['History', 'Product', 'Category']
            # Drop the tables and reset the auto increment start number.
            for table in tables:
                self.cursor.execute(drop_query.format(table))
                self.cursor.execute(reset_auto_increment.format(table))
                self.database.commit()
        except Exception as err:
            print(f'Error during droping tables:\n{err}\nexit\n')
            sys.exit(1)

    def insert_products(self, product_number, url):
        """
        Insert all products off each category into the database.

        :param product_number:  Number of product.
        :param url:             Category url.
        """
        products_query = """
            INSERT INTO Product (product_name, img_url, salt, fat,
            sugars, saturated_fat, warehouse, allergens, nutrition_grades,
            category)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        products = list()
        total_page = ceil(product_number / 20)
        # Limit to 200 products per category.
        if total_page > 10:
            total_page = 11
        page = 1
        # Browse all pages of a category.
        for page in range(1, total_page):
            print(f'Page : {page}')
            response = requests.get(f'{url}/{page}.json').json()
            # Add all products into a huge list.
            products += [
                (
                    p.get('product_name'),
                    p.get('image_url'),
                    p['nutrient_levels'].get('salt'),
                    p['nutrient_levels'].get('fat'),
                    p['nutrient_levels'].get('sugars'),
                    p['nutrient_levels'].get('saturated-fat'),
                    p.get('brands'),
                    p.get('allergens'),
                    p.get('nutrition_grades'),
                    self.category_id
                )
                for p in response['products']
            ]
        # Insert all the products for a category into 'Product' table.
        try:
            self.cursor.executemany(products_query, products)
            self.database.commit()
        except Exception as e:
            print(f'Error during product insertion:\n{e}\n')
            sys.exit(1)

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
        except Exception as e:
            print(f'Error during category insertion:\n{e}\nexit\n')
            sys.exit(1)

    def update_database(self):
        """
        Update the database.
        """
        categories_url = 'https://fr.openfoodfacts.org/categories.json'
        response = requests.get(categories_url).json()
        # Browse all categories.
        print('Database sync started..')
        print(100 * '=')
        self.drop_tables()
        for category_number, category in enumerate(response['tags']):
            self.insert_category(category['name'])
            self.insert_products(category['products'], category['url'])
            if category_number == 20:
                break
            print(100 * '=')
        self.cursor.close()
        self.database.close()
        print("Database sync finished")
