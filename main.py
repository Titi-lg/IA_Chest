import sys
from test_connect4 import main as test_connect4
from test_chess import main as test_chess

def main():
    print("Choisissez un jeu :")
    print("1. Connect4")
    print("2. Échecs")
    
    choice = input("Votre choix (1, 2): ")
    
    if choice == "1":
        test_connect4()
    elif choice == "2":
        test_chess()
    else:
        print("Choix invalide")
        sys.exit()

if __name__ == "__main__":
    main()
