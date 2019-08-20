MESSAGE_PROMPT = '-------------------------------------------\n'\
    '1 - Quel aliment souhaitez-vous remplacer ?\n'\
    '2 - Retrouver mes aliments substitués.\n'\
    '3 - Synchroniser la base de données.\n'\
    'Q - Quitter.\n'\
    '-------------------------------------------\n'


CATEGORIES_URL = 'https://fr.openfoodfacts.org/categories.json'

CINFO = {
    'host': 'localhost',
    'user': 'vagrant',
    'passwd': '1234',
    'database': 'openfoodfacts'
}

SHOW_PRODUCT_PROMPT = ('\n\ns - find a subtitute | p - previous page | r -'
                        ' register\n\nQ - Quitter.\n\n')