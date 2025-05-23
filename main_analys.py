import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import test_chess as tc
import test_connect4 as tc4
import IA.alphabeta as alpha
import IA.minimax as mini
import IA.mcts as mcts
import time
import concurrent.futures
from tqdm import tqdm
import threading


# Get the appropriate parameter based on algorithm type
def get_algo_param(algo):
    if algo.__class__.__name__ == "MCTS":
        return f"{algo.__class__.__name__}_{algo.thinking_time}"
    else:
        return f"{algo.__class__.__name__}_{algo.max_depth}"

# Function to play a single game (for threading)
def play_single_game(game_type, algo1, algo2, game_idx):
    if game_type == 'chess':
        player, nb_move = tc.play_game(algo1, algo2, verbose=False)
    elif game_type == 'connect4':
        player, nb_move = tc4.play_game(algo1, algo2, verbose=False)
    else:
        raise ValueError("Unsupported game type")
    
    print(player, nb_move)
    
    return {
        'game': game_type,
        'algo1': get_algo_param(algo1),
        'algo2': get_algo_param(algo2),
        'winner': algo1.__class__.__name__ if player == 1 else algo2.__class__.__name__ if player == 2 else 'draw',
        'nb_move': nb_move
    }


if __name__ == '__main__':

    # Variables
    game = 'chess'

    algorithms = [
        alpha.Alphabeta(1),
        mini.Minimax(1),
        mcts.MCTS(1000),
        alpha.Alphabeta(2),
        mini.Minimax(2),
        mcts.MCTS(2000),
        alpha.Alphabeta(3),
        mini.Minimax(3),
        #mcts.MCTS(300),
        #alpha.Alphabeta(4),
        #mini.Minimax(4),
        #mcts.MCTS(400),
        #alpha.Alphabeta(5),
        #mcts.MCTS(500),
        #mcts.MCTS(600),
        #mcts.MCTS(700),
        #mcts.MCTS(800),
        #mcts.MCTS(900),
        #mcts.MCTS(1000),
    ]
    
    nb_games = 3

    results = []
    results_lock = threading.Lock()  # For thread-safe access to results list

    # Main 
    # Prepare all game combinations
    all_games = []
    for algo1 in algorithms:
        for algo2 in algorithms:
            if algo1 == algo2:
                continue
            for i in range(nb_games):
                all_games.append((game, algo1, algo2, i))
    
    # Run games in parallel with a progress bar
    with concurrent.futures.ThreadPoolExecutor(max_workers=11) as executor:
        futures = [executor.submit(play_single_game, g, a1, a2, i) for g, a1, a2, i in all_games]
        
        for f in tqdm(concurrent.futures.as_completed(futures), total=len(futures), 
                      desc="Playing Games", unit="game"):
            try:
                result = f.result()
                #with results_lock:
                #    results.append(result)
                    
                    # Save intermediate results every 50 games to avoid losing progress
                    #if len(results) % 50 == 0:
                    #    temp_df = pd.DataFrame(results)
                    #    temp_df.to_csv(f"results_{game}_intermediate.csv", index=False)

            except Exception as e:
                # Get information about which algorithms were playing
                try:
                    # Convert to standard Python int to avoid NumPy integer compatibility issues
                    idx = futures.index(f)
                    game_info = all_games[idx]
                    algo1_name = get_algo_param(game_info[1])
                    algo2_name = get_algo_param(game_info[2])
                except (ValueError, KeyError, IndexError) as idx_err:
                    # If we can't get the index or algorithms, provide generic error
                    print(f"Error in game (could not identify algorithms): {str(e)}")
                    continue
                
                print(f"Error during game between {algo1_name} and {algo2_name}: {str(e)}")
                # Continue with other games rather than halting execution

    # If we have results despite some errors, still create the output
    if results:
        # Convert results to DataFrame
        df = pd.DataFrame(results)
        
        # Save results to CSV
        df.to_csv(f"results_{game}.csv", index=False)
        print(f"Results saved to results_{game}.csv")
    else:
        print("No successful games completed. No results to save.")





