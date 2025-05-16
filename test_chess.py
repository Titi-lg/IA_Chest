import time
from game.chess_game import ChessGame, WHITE, BLACK
from IA.alphabeta import Alphabeta
from IA.minimax import Minimax
from IA.mcts import MCTS

def display_board(board):
    """Display the chess board in text format"""
    piece_symbols = {
        0: ' ',
        1: '♙', -1: '♟',
        2: '♘', -2: '♞',
        3: '♗', -3: '♝',
        5: '♖', -5: '♜',
        9: '♕', -9: '♛',
        100: '♔', -100: '♚'
    }
    
    print("  a b c d e f g h")
    print(" +-----------------+")
    for row in range(7, -1, -1):
        print(f"{row+1}|", end="")
        for col in range(8):
            print(f" {piece_symbols[board[row][col]]}", end="")
        print(" |")
    print(" +-----------------+")

def algebraic_to_coords(move):
    """Convert algebraic notation to coordinates (simplified)"""
    file_map = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
    from_file, from_rank, to_file, to_rank = move[0], int(move[1]), move[2], int(move[3])
    return (from_rank-1, file_map[from_file]), (to_rank-1, file_map[to_file])

def coords_to_algebraic(coords):
    """Convert coordinates to algebraic notation (simplified)"""
    file_map = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}
    (from_row, from_col), (to_row, to_col) = coords
    return f"{file_map[from_col]}{from_row+1}{file_map[to_col]}{to_row+1}"

def play_game(ai1, ai2, max_moves=100, verbose=True):
    """Play a game between two AIs and return the winner"""
    game = ChessGame()
    current_player = WHITE
    moves_count = 0
    
    if verbose:
        print(f"Game: {ai1.__class__.__name__} (White) vs {ai2.__class__.__name__} (Black)")
        display_board(game.get_board())
    
    while not game.is_terminal() and moves_count < max_moves:
        start_time = time.time()
        
        if current_player == WHITE:
            move = ai1.get_move(game, current_player)
            ai_name = ai1.__class__.__name__
        else:
            move = ai2.get_move(game, current_player)
            ai_name = ai2.__class__.__name__
            
        end_time = time.time()
        
        if move == -1:
            # Game over signal
            break
            
        game.make_move(move, current_player)
        moves_count += 1
        
        if verbose:
            print(f"Move {moves_count}: Player {current_player} ({ai_name}) {coords_to_algebraic(move)} in {end_time - start_time:.3f}s")
            display_board(game.get_board())
        
        if game.check_win(current_player):
            if verbose:
                print(f"Player {current_player} ({ai_name}) wins!")
            return current_player, moves_count
        
        # Switch players
        current_player = game.get_opponent(current_player)
    
    if game.is_terminal() and verbose:
        print("Game over!")
        if game._is_in_check(WHITE):
            print("Black wins by checkmate!")
            return BLACK, moves_count
        elif game._is_in_check(BLACK):
            print("White wins by checkmate!")
            return WHITE, moves_count
        else:
            print("Draw!")
    
    if moves_count >= max_moves and verbose:
        print("Game reached move limit!")
    
    return 0, moves_count  # 0 for draw

def human_vs_ai():
    game = ChessGame()
    current_player = WHITE
    
    print("Choose AI algorithm:")
    print("1. Minimax (Depth 2)")
    print("2. Alpha-Beta (Depth 2)")
    print("3. MCTS (200ms)")
    
    choice = input("Your choice (1/2/3): ")
    
    if choice == "1":
        ai = Minimax(2)
    elif choice == "2":
        ai = Alphabeta(2)
    elif choice == "3":
        ai = MCTS(200)  # 200ms thinking time
    else:
        print("Invalid choice, using Alpha-Beta")
        ai = Alphabeta(2)
    
    print("You are playing as White (uppercase pieces)")
    print("Enter moves in simple algebraic notation, e.g. 'e2e4'")
    display_board(game.get_board())
    
    while not game.is_terminal():
        if current_player == WHITE:  # Human's turn
            valid_moves = game.get_valid_moves()
            move_str = input("Your move: ")
            try:
                move = algebraic_to_coords(move_str)
                if move not in valid_moves:
                    print("Invalid move! Try again.")
                    continue
            except:
                print("Please enter a valid move in format 'e2e4'")
                continue
        else:  # AI's turn
            print("AI is thinking...")
            start_time = time.time()
            move = ai.get_move(game, current_player)
            end_time = time.time()
            print(f"AI chose {coords_to_algebraic(move)} in {end_time - start_time:.3f}s")
        
        game.make_move(move, current_player)
        display_board(game.get_board())
        
        if game.check_win(current_player):
            if current_player == WHITE:
                print("Congratulations! You win!")
            else:
                print("AI wins this time!")
            return
        
        # Switch players
        current_player = game.get_opponent(current_player)
    
    print("Game over!")
    if game._is_in_check(WHITE):
        print("Black (AI) wins by checkmate!")
    elif game._is_in_check(BLACK):
        print("White (You) win by checkmate!")
    else:
        print("It's a draw!")

def main():
    print("Chess AI Testing")
    print("================")
    
    print("\nOptions:")
    print("1. Single AI vs AI match")
    print("2. Human vs AI")
    
    choice = input("Choose option (1/2): ")
    
    if choice == '1':
        print("Choose algorithms:")
        print("1. Minimax")
        print("2. Alpha-Beta")
        print("3. MCTS")
        
        choice1 = input("First AI (1/2/3): ")
        depth1 = int(input("First AI depth/time (1-3 or ms): "))
        
        choice2 = input("Second AI (1/2/3): ")
        depth2 = int(input("Second AI depth/time (1-3 or ms): "))
        
        # Create AIs
        if choice1 == "1":
            ai1 = Minimax(depth1)
        elif choice1 == "2":
            ai1 = Alphabeta(depth1)
        elif choice1 == "3":
            ai1 = MCTS(depth1)
            
        if choice2 == "1":
            ai2 = Minimax(depth2)
        elif choice2 == "2":
            ai2 = Alphabeta(depth2)
        elif choice2 == "3":
            ai2 = MCTS(depth2)
        
        # Play game
        play_game(ai1, ai2, verbose=True)
    
    elif choice == '2':
        # Human vs AI
        human_vs_ai()
    
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
