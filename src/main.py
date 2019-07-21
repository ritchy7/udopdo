from getpass import getpass


def ask_for_choice():
    """
    Ask for choice in the main menu.
    """
    while True:
        try:
            message_prompt = '-------------------------------------------\n'\
                             '1 - Quel aliment souhaitez-vous remplacer ?\n'\
                             '2 - Retrouver mes aliments substitués.\n'\
                             '3 - Synchroniser la base de donnée\n'\
                             'q - Quitter.\n'\
                             '-------------------------------------------\n'
            choice = getpass(prompt=message_prompt)
            if choice == '1':
                print('C\'est gagné ! 1')
            elif choice == '2':
                print('C\'est gagné ! 2')
            elif choice == '3':
                print('c\'est gagné ! 3')
            elif choice == 'q':
                print('\nFermeture du logiciel\n')
                exit()
            else:
                raise ValueError
        except ValueError:
            print(f'\'{choice}\' n\'est pas valide.\n')


if __name__ == '__main__':
    ask_for_choice()
