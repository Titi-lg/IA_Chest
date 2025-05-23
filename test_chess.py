import time
import concurrent.futures
from game.chess_game import ChessGame, WHITE, BLACK
from IA.alphabeta import Alphabeta
from IA.minimax import Minimax
from IA.mcts import MCTS
from view.chessView import ChessGUI

# Try to import tqdm for progress bar
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    print("Tip: Install 'tqdm' package for progress bars (pip install tqdm)")

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
    
    # Collect performance data
    total_time_white = 0
    total_time_black = 0
    
    while not game.is_terminal() and moves_count < max_moves:
        start_time = time.time()
        
        if current_player == WHITE:
            move = ai1.get_move(game, current_player)
            ai_name = ai1.__class__.__name__
            total_time_white += time.time() - start_time
        else:
            move = ai2.get_move(game, current_player)
            ai_name = ai2.__class__.__name__
            total_time_black += time.time() - start_time
            
        end_time = time.time()
        
        if move == -1:
            # Game over signal
            break
            
        game.make_move(move, current_player)
        moves_count += 1
        
        if verbose:
            print(f"Move {moves_count}: Player {current_player} ({ai_name}) {coords_to_algebraic(move)} in {end_time - start_time:.3f}s")
            display_board(game.get_board())
            
            # Print move cache stats every 10 moves
            if moves_count % 10 == 0:
                print(f"Move cache - Hits: {game.cache_hits}, Misses: {game.cache_misses}")
        
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
    
    # Print performance summary
    if verbose:
        print(f"Performance summary:")
        print(f"White (AI1) total thinking time: {total_time_white:.2f}s")
        print(f"Black (AI2) total thinking time: {total_time_black:.2f}s")
        print(f"Total game time: {total_time_white + total_time_black:.2f}s")
        print(f"Move cache - Hits: {game.cache_hits}, Misses: {game.cache_misses}")
    
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
    import tkinter as tk
    import tkinter.messagebox
    root = tk.Tk()
    app = ChessGUI(root, ai_player=BLACK, ai_algo=2)  # Humain = blanc, IA = noir
    root.mainloop()

# Move play_single_game outside of play_tournament to make it picklable
def play_single_game(pair):
    """Play a single game between two AIs"""
    ai1, ai2 = pair
    return (ai1.__class__.__name__, ai2.__class__.__name__, play_game(ai1, ai2, 100, verbose=False))

def play_tournament(ai_list, games_per_matchup=2, max_moves=100):
    """Play a tournament between several AIs"""
    results = {}
    for ai1 in ai_list:
        for ai2 in ai_list:
            if ai1 is not ai2:  # Don't play against self
                key = (ai1.__class__.__name__, ai2.__class__.__name__)
                results[key] = {"wins": 0, "losses": 0, "draws": 0, "moves": 0}
    
    # Play games in parallel
    game_pairs = []
    for ai1 in ai_list:
        for ai2 in ai_list:
            if ai1 is not ai2:
                for _ in range(games_per_matchup):
                    game_pairs.append((ai1, ai2))
    
    # Calculate total games for progress bar
    total_games = len(game_pairs)
    print(f"Starting tournament with {total_games} games...")
    
    # Play games in parallel
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [executor.submit(play_single_game, pair) for pair in game_pairs]
        
        # Setup progress bar if available
        if TQDM_AVAILABLE:
            futures_iterator = tqdm(
                concurrent.futures.as_completed(futures),
                total=len(futures),
                desc="Tournament Progress",
                unit="game"
            )
        else:
            # Simple progress reporting if tqdm is not available
            futures_iterator = concurrent.futures.as_completed(futures)
            completed = 0
            
        # Process results as they complete
        for future in futures_iterator:
            try:
                ai1_name, ai2_name, (winner, moves) = future.result()
                key = (ai1_name, ai2_name)
                
                # Update results
                if winner == WHITE:
                    results[key]["wins"] += 1
                elif winner == BLACK:
                    results[key]["losses"] += 1
                else:
                    results[key]["draws"] += 1
                results[key]["moves"] += moves
                
                # Simple progress reporting if tqdm is not available
                if not TQDM_AVAILABLE:
                    completed += 1
                    if completed % 5 == 0 or completed == total_games:
                        print(f"Progress: {completed}/{total_games} games completed ({(completed/total_games)*100:.1f}%)")
                
            except Exception as e:
                print(f"Error in game: {e}")
    
    # Print tournament results
    print("\nTournament Results:")
    print("==================")
    for (ai1_name, ai2_name), stats in results.items():
        avg_moves = stats["moves"] / games_per_matchup
        print(f"{ai1_name} vs {ai2_name}: Wins: {stats['wins']}, Losses: {stats['losses']}, Draws: {stats['draws']}, Avg Moves: {avg_moves:.1f}")
    
    return results

# Add a sequential tournament function with progress bar as fallback
def play_tournament_sequential(ai_list, games_per_matchup=2, max_moves=100):
    """Play a tournament between several AIs sequentially with progress bar"""
    results = {}
    game_pairs = []
    
    # Setup the matchups
    for ai1 in ai_list:
        for ai2 in ai_list:
            if ai1 is not ai2:  # Don't play against self
                key = (ai1.__class__.__name__, ai2.__class__.__name__)
                results[key] = {"wins": 0, "losses": 0, "draws": 0, "moves": 0}
                
                # Add all games for this matchup
                for _ in range(games_per_matchup):
                    game_pairs.append((ai1, ai2))
    
    # Play each game with progress bar
    total_games = len(game_pairs)
    print(f"Starting tournament with {total_games} games sequentially...")
    
    if TQDM_AVAILABLE:
        game_iterator = tqdm(game_pairs, desc="Tournament Progress", unit="game")
    else:
        game_iterator = game_pairs
        
    for i, (ai1, ai2) in enumerate(game_iterator):
        ai1_name = ai1.__class__.__name__
        ai2_name = ai2.__class__.__name__
        
        # Play the game
        winner, moves = play_game(ai1, ai2, max_moves, verbose=False)
        
        # Update results
        key = (ai1_name, ai2_name)
        if winner == WHITE:
            results[key]["wins"] += 1
        elif winner == BLACK:
            results[key]["losses"] += 1
        else:
            results[key]["draws"] += 1
        results[key]["moves"] += moves
        
        # Report progress without tqdm
        if not TQDM_AVAILABLE and (i+1) % 5 == 0:
            print(f"Progress: {i+1}/{total_games} games completed ({((i+1)/total_games)*100:.1f}%)")
    
    # Print tournament results
    print("\nTournament Results:")
    print("==================")
    for (ai1_name, ai2_name), stats in results.items():
        avg_moves = stats["moves"] / games_per_matchup
        print(f"{ai1_name} vs {ai2_name}: Wins: {stats['wins']}, Losses: {stats['losses']}, Draws: {stats['draws']}, Avg Moves: {avg_moves:.1f}")
    
    return results

def main():
    print("Chess AI Testing")
    print("================")
    
    print("\nOptions:")
    print("1. Single AI vs AI match")
    print("2. Human vs AI")
    print("3. AI Tournament")
    
    choice = input("Choose option (1/2/3): ")
    
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
    
    elif choice == '3':
        # Tournament mode
        print("Running tournament with optimized AIs")
        ai_list = [
            Minimax(2),
            Alphabeta(2),
            MCTS(200)
        ]
        
        # Ask for tournament type
        print("\nTournament type:")
        print("1. Parallel (faster but may have issues)")
        print("2. Sequential (slower but more stable)")
        tourney_type = input("Choose type (1/2): ")
        
        try:
            if tourney_type == "2":
                play_tournament_sequential(ai_list, games_per_matchup=2, max_moves=50)
            else:
                play_tournament(ai_list, games_per_matchup=2, max_moves=50)
        except Exception as e:
            print(f"Error with parallel tournament: {e}")
            print("Falling back to sequential tournament...")
            play_tournament_sequential(ai_list, games_per_matchup=2, max_moves=50)
    
    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
