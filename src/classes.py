from constant import MESSAGE_PROMPT
from math import ceil
from mysql.connector import connect
from colorama import (
    Back,
    Fore,
    init,
    Style
)
import requests
import sys


# Coloration
init(autoreset=True)


class OpenFoodFacts:

    def __init__(self, cinfo):
        self.category_id = None
        self.main_menu_choice = None
        self.cinfo = cinfo
        self.cursor = None
        self.database = None
        self.products = None

    def init_connection(self):
        """
        Initalize the connection.
        """
        # Init the connection with the database.
        try:
            self.database = connect(**self.cinfo)
            self.cursor = self.database.cursor(buffered=True)
        except Exception as err:
            print(f'{Fore.RED}Error during the connection:\n{err}\nexit\n')
            sys.exit(1)

    def quit(self):
        """
        Exit the program.
        """
        print(f'{Fore.YELLOW}\nYou\'ve decided to leave\nBye bye\n')
        sys.exit(0)

    def drop_tables(self):
        """
        drop all tables.
        """
        try:
            query = 'DELETE FROM {0};'
            reset_auto_increment = 'ALTER TABLE {0} AUTO_INCREMENT = 1;'
            tables = ['History', 'Product', 'Category']
            # Drop the tables and reset the auto increment start number to 1.
            for table in tables:
                self.cursor.execute(query.format(table))
                self.cursor.execute(reset_auto_increment.format(table))
                self.database.commit()
        except Exception as err:
            print(f'{Fore.RED}Error during droping tables:\n{err}\nexit\n')
            sys.exit(1)

    def update_database(self):
        """
        Update the database.
        """
        categories_url = 'https://fr.openfoodfacts.org/categories.json'
        response = requests.get(categories_url).json()
        # Browse all categories.
        print(f'{Fore.GREEN}Database sync started..')
        print(100 * '=')
        # Clean the database.
        self.drop_tables()
        # Re-insert all categories and their products in the database.
        for category_number, category in enumerate(response['tags']):
            self.insert_category(category['name'])
            self.insert_products(category['products'], category['url'])
            # Limit category number to 20.
            if category_number == 20:
                break
            print(100 * '=')
        self.cursor.close()
        self.database.close()
        print(f'{Fore.GREEN}Database sync finished')

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
            elif main_menu_choice == 'Q':
                self.quit()
            else:
                print(f'{Fore.RED}\'{main_menu_choice}\' is not valid.\n')

    def category_selection_menu(self):
        """
        Select a category.
        """
        self.cursor.execute('SELECT * FROM Category;')
        categories = '\n'.join([
            f'{k} - {v}' for k, v in dict(self.cursor.fetchall()).items()
        ])
        menu_message = f'Select a category :\n{categories}\n\nQ - Quitter.\n\n'
        query = 'SELECT * FROM Product WHERE category = {};'
        # Show all categories.
        while True:
            print(50 * '-')
            menu_choice = input(menu_message)
            if menu_choice == 'Q':
                self.quit()
            elif menu_choice not in categories:
                print(f'{Fore.RED}category number {menu_choice} is not valid')
            else:
                # Show all products in a category.
                try:
                    self.cursor.execute(query.format(menu_choice))
                    self.products = [{
                        'id': p[0], 'name': p[1], 'img': p[2], 'salt': p[3],
                        'fat': p[4], 'sugars': p[5], 'saturated_fat': p[6],
                        'warehouse': p[7], 'allergens': p[8],
                        'nutrition grades': p[9]
                    } for p in self.cursor.fetchall()]
                    self.cursor.close()
                    self.database.commit()
                    self.product_selection_menu()
                except Exception as e:
                    print(f'{Fore.RED}Error during category selection: {e}')
                self.init_connection()

    def product_selection_menu(self):
        """
        Select a product.
        """
        max_page = len(self.products)
        # Show all products per pagination.
        start = 0
        end = 10
        while True:
            print(50 * '-')
            message_products = '\n'.join([
                f"{p['id']} - {p['name']}" for p in self.products[start:end]
            ])
            menu_message = f'Select a product:\n{message_products}\n\n'
            menu_message += f'p - previous page | n - next page\n\n'
            menu_message += f'P - Back to categorie menu\nQ - Quitter.\n\n'
            menu_choice = input(menu_message)
            if menu_choice == 'Q':
                self.quit()
            elif menu_choice == 'P':
                break
            elif menu_choice == 'n':
                end, start = end + 10, start + 10
                if end > max_page:
                    end, start = max_page, max_page - 10
            elif menu_choice == 'p':
                end, start = end - 10, start - 10
                if start < 0:
                    end, start = 10, 0
            else:
                try:
                    product = next(
                        product
                        for product in self.products
                        if product['id'] == int(menu_choice)
                    )
                    self.show_product(product)
                except Exception as e:
                    print(f'{Fore.RED}{menu_choice} not exist in product list')

    def show_product(self, product):
        """
        Show the describe of a product.

        :param product (dict):  Product description.
        """
        product_description = '\n'.join(
            [f"{k} - {v}" for k, v in product.items()]
        )
        menu_message = f'{product_description}\n\ns - find a subtitute | '
        menu_message += 'p - previous page | r - register\n\nQ - Quitter.\n\n'
        query = 'INSERT IGNORE INTO History (product_id) VALUES({});'
        while True:
            menu_choice = input(menu_message)
            if menu_choice == 'p':
                break
            elif menu_choice == 'Q':
                self.quit()
            elif menu_choice == 's':
                self.show_substitute(product['id'])
            elif menu_choice == 'r':
                try:
                    self.init_connection()
                    self.cursor.execute(query.format(product['id']))
                    self.database.commit()
                    self.cursor.close()
                    self.database.close()
                    print(f"{Fore.GREEN}Product {product['id']} registered !\n")
                    break
                except Exception as e:
                    print(f'{Fore.RED}Error during saving product:\n{e}\n')
            else:
                print(f'{Fore.RED}{menu_choice} is an invalid input.')

    def show_substitute(self, product_id):
        """
        Show a better product than the one chosen.

        :param product_id (int):   Product id.
        """
        pass

    def insert_products(self, product_number, url):
        """
        Insert all products off each category into the database.

        :param product_number (string):  Number of product.
        :param url (string):             Category url.
        """
        query = """
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
            products += [(
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
            ) for p in response['products']]
        # Insert all the products for a category into 'Product' table.
        try:
            self.cursor.executemany(query, products)
            self.database.commit()
        except Exception as e:
            print(f'{Fore.RED}Error during product insertion:\n{e}\n')
            sys.exit(1)

    def insert_category(self, category_name):
        """
        Insert a category into the database.

        :param category_name (string):   category's name.
        """
        query = 'INSERT INTO Category (category_name) VALUES (%s);'
        try:
            # Insert category into the database.
            self.cursor.execute(query, (category_name,))
            self.category_id = self.cursor.lastrowid
            print(f'{Fore.YELLOW}Category {category_name} sync in progress..')
        except Exception as e:
            print(f'{Fore.RED}Error during category insertion:\n{e}\nexit\n')
            sys.exit(1)
