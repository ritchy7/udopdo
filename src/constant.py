# Main menu message prompt.
MESSAGE_PROMPT = ('-------------------------------------------\n'
                  '1 - Quel aliment souhaitez-vous remplacer ?\n'
                  '2 - Retrouver mes aliments substitués.\n'
                  '3 - Synchroniser la base de données.\n'
                  'Q - Quitter.\n'
                  '-------------------------------------------\n')

# Categories url.
CATEGORIES_URL = 'https://fr.openfoodfacts.org/categories.json'

# Connexion informations.
CINFO = {
    'host': 'localhost',
    'user': 'vagrant',
    'passwd': '1234',
    'database': 'openfoodfacts'
}

# Selection product prompt message.
PRODUCT_PROMPT = ('\n\ns - find a subtitute | p - previous page | r -'
                  ' register\n\nQ - Quitter.\n\n')

#  History product prompt message.
PRODUCT_PROMPT_HISTORICAL = ('\n\nd - delete the product | P - back to'
                             ' history\n\n')

# Query to retrieve all product choiced.
GET_HISTORY_QUERY = '''
    SELECT
        Product.id,
        Product.product_name,
        Product.product_url,
        Product.salt,
        Product.fat,
        Product.sugars,
        Product.saturated_fat,
        Product.warehouse,
        Product.allergens,
        Product.nutrition_grades
    FROM Product
    RIGHT JOIN History
    ON Product.id = History.product_id;
'''
