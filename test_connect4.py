import time
from game.connect4_game import Connect4Game
from IA.alphabeta import Alphabeta
from IA.minimax import Minimax
from IA.mcts import MCTS  # Import directly - no need for try/except now

def display_board(board):
    """Display the Connect4 board in text format"""
    print()
    for row in range(len(board)-1, -1, -1):
        print('|', end='')
        for col in range(len(board[0])):
            if board[row][col] == 0:
                print('   |', end='')
            elif board[row][col] == 1:
                print(' X |', end='')
            else:
                print(' O |', end='')
        print()
    
    print('|', end='')
    for i in range(len(board[0])):
        print(f' {i} |', end='')
    print("\n")

def play_game(ai1, ai2, verbose=True):
    """Play a game between two AIs and return the winner"""
    game = Connect4Game()
    current_player = 1
    moves_count = 0
    
    if verbose:
        print(f"Game: {ai1.__class__.__name__} (X) vs {ai2.__class__.__name__} (O)")
        display_board(game.get_board())
    
    while not game.is_terminal():
        start_time = time.time()
        
        if current_player == 1:
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
            print(f"Player {current_player} ({ai_name}) chose column {move} in {end_time - start_time:.3f}s")
            display_board(game.get_board())
        
        if game.check_win(current_player):
            if verbose:
                print(f"Player {current_player} ({ai_name}) wins!")
            return current_player, moves_count
        
        # Switch players
        current_player = game.get_opponent(current_player)
    
    if verbose:
        print("It's a draw!")
    return 0, moves_count  # 0 for draw

def tournament(algorithms, num_iterations=5, verbose=False):
    """Run a ladder tournament with Bo3 matches"""
    # Initialize rankings and results
    rankings = list(range(len(algorithms)))  # Initial ranking
    results = {algo.__class__.__name__: {'wins': 0, 'draws': 0, 'losses': 0} for algo in algorithms}
    total_moves = {algo.__class__.__name__: 0 for algo in algorithms}
    
    # Run tournament for specified number of iterations
    for iteration in range(num_iterations):
        print(f"\n=== Tournament Iteration {iteration+1}/{num_iterations} ===")
        print("Current Ranking:")
        for rank, idx in enumerate(rankings):
            print(f"{rank+1}. {algorithms[idx].__class__.__name__}")
        
        # For each position except the top one
        for pos in range(len(rankings)-1):
            # Get the algorithms at current and next position
            algo_idx_lower = rankings[pos+1]
            algo_idx_higher = rankings[pos]
            
            algo_lower = algorithms[algo_idx_lower]
            algo_higher = algorithms[algo_idx_higher]
            
            algo_lower_name = algo_lower.__class__.__name__
            algo_higher_name = algo_higher.__class__.__name__
            
            print(f"\nMatch: {algo_lower_name} vs {algo_higher_name} (Bo3)")
            
            # Play best of 3
            lower_wins = 0
            higher_wins = 0
            games_played = 0
            total_match_moves = 0
            
            while games_played < 3 and lower_wins < 2 and higher_wins < 2:
                # Alternate who goes first
                if games_played % 2 == 0:
                    # Lower ranked algo goes first
                    winner, moves = play_game(algo_lower, algo_higher, verbose)
                    
                    if winner == 1:  # Lower ranked won
                        lower_wins += 1
                        results[algo_lower_name]['wins'] += 1
                        results[algo_higher_name]['losses'] += 1
                        print(f"Game {games_played+1}: {algo_lower_name} wins")
                    elif winner == 2:  # Higher ranked won
                        higher_wins += 1
                        results[algo_higher_name]['wins'] += 1
                        results[algo_lower_name]['losses'] += 1
                        print(f"Game {games_played+1}: {algo_higher_name} wins")
                    else:  # Draw
                        results[algo_lower_name]['draws'] += 1
                        results[algo_higher_name]['draws'] += 1
                        print(f"Game {games_played+1}: Draw")
                else:
                    # Higher ranked algo goes first
                    winner, moves = play_game(algo_higher, algo_lower, verbose)
                    
                    if winner == 1:  # Higher ranked won
                        higher_wins += 1
                        results[algo_higher_name]['wins'] += 1
                        results[algo_lower_name]['losses'] += 1
                        print(f"Game {games_played+1}: {algo_higher_name} wins")
                    elif winner == 2:  # Lower ranked won
                        lower_wins += 1
                        results[algo_lower_name]['wins'] += 1
                        results[algo_higher_name]['losses'] += 1
                        print(f"Game {games_played+1}: {algo_lower_name} wins")
                    else:  # Draw
                        results[algo_lower_name]['draws'] += 1
                        results[algo_higher_name]['draws'] += 1
                        print(f"Game {games_played+1}: Draw")
                
                games_played += 1
                total_match_moves += moves
            
            # Record moves
            total_moves[algo_higher_name] += total_match_moves // 2
            total_moves[algo_lower_name] += total_match_moves // 2
            
            # Print match result
            print(f"Match result: {algo_lower_name} {lower_wins} - {higher_wins} {algo_higher_name}")
            
            # If the lower-ranked algorithm won, swap positions
            if lower_wins > higher_wins:
                print(f"{algo_lower_name} wins the match and moves up!")
                rankings[pos], rankings[pos+1] = rankings[pos+1], rankings[pos]
            else:
                print(f"{algo_higher_name} maintains position.")
    
    # Print final tournament results
    print(f"\n=== Final Ranking ===")
    for rank, idx in enumerate(rankings):
        print(f"{rank+1}. {algorithms[idx].__class__.__name__}")
    
    print(f"\n=== Tournament Statistics ===")
    print(f"{'Algorithm':<15} {'Wins':<8} {'Draws':<8} {'Losses':<8} {'Win %':<8} {'Avg Moves':<12}")
    print("-" * 60)
    
    for algo_name, stats in results.items():
        games = stats['wins'] + stats['draws'] + stats['losses']
        if games > 0:
            win_percentage = (stats['wins'] + stats['draws'] * 0.5) / games * 100
            avg_moves = total_moves[algo_name] / games if games > 0 else 0
            print(f"{algo_name:<15} {stats['wins']:<8} {stats['draws']:<8} {stats['losses']:<8} {win_percentage:.1f}%    {avg_moves:.1f}")
    
    return rankings, results

def main():
    print("Connect4 AI Testing")
    print("===================")
    
    # Create AI instances with different depths/parameters
    algorithms = [
        Minimax(2),
        Minimax(3),
        Alphabeta(3),
        Alphabeta(4),
        MCTS(200)  # 200 ms thinking time
    ]
    
    # Display algorithm options
    print("\nAvailable algorithms:")
    for i, algo in enumerate(algorithms):
        if hasattr(algo, 'max_depth'):
            print(f"{i+1}. {algo.__class__.__name__} (Depth: {algo.max_depth})")
        else:
            print(f"{i+1}. {algo.__class__.__name__} (Time: {algo.thinking_time*1000:.0f}ms)")
    
    print("\nOptions:")
    print("1. Single AI vs AI match")
    print("2. Run tournament between all algorithms")
    print("3. Human vs AI")
    
    choice = input("Choose option (1/2/3): ")
    
    if choice == '1':
        # Single match
        print("\nChoose algorithms for the match:")
        ai1_idx = int(input("First AI (player 1): ")) - 1
        ai2_idx = int(input("Second AI (player 2): ")) - 1
        
        if 0 <= ai1_idx < len(algorithms) and 0 <= ai2_idx < len(algorithms):
            play_game(algorithms[ai1_idx], algorithms[ai2_idx], verbose=True)
        else:
            print("Invalid algorithm selection")
    
    elif choice == '2':
        # Tournament
        num_iterations = int(input("Number of tournament iterations: "))
        verbose = input("Show detailed game information? (y/n): ").lower() == 'y'
        
        tournament(algorithms, num_iterations=num_iterations, verbose=verbose)
    
    elif choice == '3':
        # Human vs AI
        ai_idx = int(input("Choose AI opponent: ")) - 1
        
        if 0 <= ai_idx < len(algorithms):
            human_vs_ai(algorithms[ai_idx])
        else:
            print("Invalid algorithm selection")
    
    else:
        print("Invalid choice")

def human_vs_ai(ai):
    """Play a game where human plays against the chosen AI"""
    game = Connect4Game()
    current_player = 1  # Human starts as player 1
    
    print(f"Playing against {ai.__class__.__name__}")
    display_board(game.get_board())
    
    while not game.is_terminal():
        if current_player == 1:  # Human's turn
            try:
                move = int(input("Your move (0-6): "))
                if move not in game.get_valid_moves():
                    print("Invalid move! Try again.")
                    continue
            except ValueError:
                print("Please enter a number between 0 and 6.")
                continue
        else:  # AI's turn
            print("AI is thinking...")
            start_time = time.time()
            move = ai.get_move(game, current_player)
            end_time = time.time()
            print(f"AI chose column {move} in {end_time - start_time:.3f}s")
        
        game.make_move(move, current_player)
        display_board(game.get_board())
        
        if game.check_win(current_player):
            if current_player == 1:
                print("Congratulations! You win!")
            else:
                print("AI wins this time!")
            return
        
        # Switch players
        current_player = game.get_opponent(current_player)
    
    print("It's a draw!")

if __name__ == "__main__":
    main()
