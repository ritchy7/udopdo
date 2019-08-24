# Python libraries.
from math import ceil
import os
import requests
import sys

# Third-party libraries.
from colorama import Fore, init
from mysql.connector import connect

# Local libraries.
from constant import (
    CATEGORIES_URL,
    MESSAGE_PROMPT,
    SHOW_PRODUCT_PROMPT
)


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
        self.clear = None
        self.unwanted = []

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
        self.clear_screen()
        print(f'{Fore.YELLOW}\nYou\'ve decided to leave\nBye bye\n')
        sys.exit(0)

    @staticmethod
    def clear_screen():
        """
        Clear the terminal.
        """
        os.system('cls' if os.name == 'nt' else 'clear')

    def drop_tables(self):
        """
        Delete the data from each table.
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
        Update the database, delete the data from each table
        and replenishing them.
        """
        # Clear Terminal.
        self.clear_screen()
        response = requests.get(CATEGORIES_URL).json()
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
        self.clear_screen()
        print(f'{Fore.GREEN}Database sync finished')

    def main_selection_menu(self):
        """
        Main selection menu.
        """
        choice = None
        self.clear = None
        while True:
            if not self.clear:
                self.clear = True
                self.clear_screen()
            choice = input(MESSAGE_PROMPT)
            if choice == '1' or choice == '2' or choice == '3':
                self.main_menu_choice = int(choice)
                break
            elif choice == 'Q':
                self.quit()
            else:
                self.clear = False
                self.clear_screen()
                print(f'{Fore.RED}\'{choice}\' is not valid.\n')

    def category_selection_menu(self):
        """
        Category selection menu.
        """
        # Get the categories from the database.
        self.cursor.execute('SELECT * FROM Category;')
        # Transform the response to a string list.
        categories = '\n'.join([
            f'{k} - {v}' for k, v in dict(self.cursor.fetchall()).items()
        ])
        menu_message = f'Select a category :\n{categories}\n\nQ - Quitter.\n\n'
        query = 'SELECT * FROM Product WHERE category_id = {};'
        error = False
        # Show all categories.
        while True:
            if not error:
                error = False
                self.clear_screen()
                print(50 * '-')
            menu_choice = input(menu_message)
            if menu_choice == 'Q':
                self.quit()
            elif menu_choice not in categories:
                error = True
                self.clear_screen()
                print(f'{Fore.RED}category number {menu_choice} is not valid')
            else:
                # Show all products in a category.
                try:
                    self.cursor.execute(query.format(menu_choice))
                    self.products = [{
                        'id': p[0], 'name': p[1], 'img': p[2], 'salt': p[3],
                        'fat': p[4], 'sugars': p[5], 'saturated_fat': p[6],
                        'warehouse': p[7], 'allergens': p[8],
                        'nutrition_grades': p[9]
                    } for p in self.cursor.fetchall()]
                    self.cursor.close()
                    self.database.commit()
                    self.product_selection_menu()
                except Exception as e:
                    error = True
                    print(f'{Fore.RED}Error during category selection:\n{e}')
                self.init_connection()

    def product_selection_menu(self):
        """
        Product selection menu, displayed in pagination.
        (20 products per page)
        """
        max_page = len(self.products)
        # Show all products per pagination.
        start = 0
        end = 20
        error = False
        while True:
            if not error:
                self.clear_screen()
                error = False
            print(50 * '-')
            message_products = '\n'.join([
                f"{p['id']} - {p['name']}" for p in self.products[start:end]
            ])
            menu_message = (f'Select a product:\n{message_products}\n\n'
                            'p - previous page | n - next page\n\n'
                            'P - Back to categorie menu\nQ - Quitter.\n\n')
            menu_choice = input(menu_message)
            if menu_choice == 'Q':
                self.quit()
            elif menu_choice == 'P':
                self.clear_screen()
                break
            elif menu_choice == 'n':
                end, start = end + 20, start + 20
                if end > max_page:
                    end, start = max_page, max_page - 20
            elif menu_choice == 'p':
                end, start = end - 20, start - 20
                if start < 0:
                    end, start = 20, 0
            else:
                try:
                    product = next(
                        product
                        for product in self.products
                        if product['id'] == int(menu_choice)
                    )
                    self.show_product(product)
                except Exception as e:
                    error = True
                    self.clear_screen()
                    print(f'{Fore.RED}{menu_choice} not exist in product list: {e}')

    def show_product(self, product):
        """
        Shows the complete description of a given product in parameter.
        (id, name, img, salt, salt, fat, sugars, satured fat, warehouse,
         allergens and nutrtion grade)

        :param product (dict):  Product description.
        """
        product_description = '\n'.join(
            [f"{k} - {v}" for k, v in product.items()]
        )
        query = 'INSERT IGNORE INTO History (product_id) VALUES({});'
        error = False
        while True:
            if not error:
                self.clear_screen()
                error = False
            menu_choice = input(product_description + SHOW_PRODUCT_PROMPT)
            if menu_choice == 'p':
                self.clear_screen()
                break
            elif menu_choice == 'Q':
                self.quit()
            elif menu_choice == 's':
                # Add product id to a list of unwanted products.
                self.unwanted.append(product['id'])
                self.show_substitute()
                break
            elif menu_choice == 'r':
                try:
                    self.init_connection()
                    self.cursor.execute(query.format(product['id']))
                    self.database.commit()
                    self.cursor.close()
                    self.database.close()
                    self.clear_screen()
                    print(f"{Fore.GREEN}Product {product['id']} registered !\n")
                    break
                except Exception as e:
                    print(f'{Fore.RED}Error during saving product:\n{e}\n')
            else:
                error = True
                self.clear_screen()
                print(f'{Fore.RED}{menu_choice} is an invalid input.')

    def show_substitute(self):
        """
        Show a better product than the one chosen.
        """
        # Sort the list by nutrition grades.
        if len(self.products) - len(self.unwanted) > 1:
            # Get products sorted by nutrition grades.
            products = [
                p for p in sorted(
                    self.products,
                    key = lambda p: p.get('nutrition_grades')
                )
                if p['id'] not in self.unwanted and p['nutrition_grades'] != ''
            ]
            # Show a substitute.
            self.show_product(products[0])

    def insert_products(self, product_number, url):
        """
        Insert all products off each category into the database.

        :param product_number (string):  Number of product.
        :param url (string):             Category url.
        """
        query = """
            INSERT INTO Product (product_name, img_url, salt, fat,
            sugars, saturated_fat, warehouse, allergens, nutrition_grades,
            category_id)
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
                p.get('product_name', ''),
                p.get('image_url', ''),
                p['nutrient_levels'].get('salt', ''),
                p['nutrient_levels'].get('fat', ''),
                p['nutrient_levels'].get('sugars', ''),
                p['nutrient_levels'].get('saturated-fat', ''),
                p.get('brands', ''),
                p.get('allergens', ''),
                p.get('nutrition_grades', ''),
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
