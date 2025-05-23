from copy import deepcopy
from random import randint

class Alphabeta:
    def __init__(self, max_depth):
        self.max_depth = max_depth
        # Add a transposition table to cache positions
        self.transposition_table = {}
        # Add killer moves table
        self.killer_moves = [[None, None] for _ in range(20)]  # Store 2 killer moves per depth
        # Add history table for move ordering
        self.history_table = {}
        # Stats for optimization monitoring
        self.nodes_evaluated = 0
        self.tt_hits = 0
        self.pruning_count = 0

    def get_move(self, game, player):        
        valid_moves = game.get_valid_moves()
        best_move = None
        best_score = float('-inf')
        alpha = float('-inf')
        beta = float('+inf')
        
        # Clear the tables for a new search
        self.transposition_table = {}
        self.killer_moves = [[None, None] for _ in range(self.max_depth + 1)]
        self.history_table = {}
        self.nodes_evaluated = 0
        self.tt_hits = 0
        self.pruning_count = 0

        # Order moves for initial search
        ordered_moves = self.order_moves(game, valid_moves, player, 0)
        
        for move in ordered_moves:
            temp_game = game.clone()
            temp_game.make_move(move, player)
            score = self.alphabeta(temp_game, self.max_depth, False, player, alpha, beta, 1)
            
            if score >= best_score:
                if score == best_score:
                    # Add randomness to equal-score moves
                    if randint(0,5) == 0:
                        best_move = move
                else:
                    best_score = score
                    alpha = score
                    best_move = move
                    
            # Remember good moves
            self.history_table[move] = self.history_table.get(move, 0) + (2 ** self.max_depth)
                    
        if best_move is None:
            if not valid_moves:
                return -1  # Game over
            return valid_moves[0]  # Choose first available move
        
        # Print statistics if requested
        # print(f"Nodes evaluated: {self.nodes_evaluated}, TT hits: {self.tt_hits}, Prunings: {self.pruning_count}")
        
        return best_move         

    def alphabeta(self, game, depth, tour_max, player, alpha, beta, ply):
        """
        Enhanced alpha-beta with move ordering and killer moves
        ply: the current depth in the search tree (starts at 1)
        """
        self.nodes_evaluated += 1
        
        # Check if terminal state or max depth reached
        if depth == 0 or game.is_terminal():
            return game.evaluate(player)
        
        # Create a hash key for the current position - handle both NumPy arrays and lists
        if hasattr(game.board, 'tobytes'):
            board_hash = str(game.board.tobytes())
        else:
            board_hash = str(game.board)
        state_key = (board_hash, depth, tour_max, player)
        
        # Check if position is in transposition table
        if state_key in self.transposition_table:
            self.tt_hits += 1
            return self.transposition_table[state_key]

        valid_moves = game.get_valid_moves()
        
        # Order moves for better pruning
        ordered_moves = self.order_moves(game, valid_moves, 
                                         player if tour_max else game.get_opponent(player), 
                                         ply)
        
        if tour_max:
            best_score = float('-inf')
            
            for move in ordered_moves:
                temp_game = game.clone()
                temp_game.make_move(move, player)
                score = self.alphabeta(temp_game, depth-1, False, player, alpha, beta, ply+1)
                best_score = max(score, best_score)
                alpha = max(alpha, best_score)
                
                # If this move caused a cutoff, it's a potential killer move
                if beta <= alpha:
                    self.record_killer_move(move, ply)
                    self.pruning_count += 1
                    break
                
                # Update history heuristic based on how good this move is
                if score > alpha:
                    self.history_table[move] = self.history_table.get(move, 0) + (2 ** depth)
            
            # Store the result in the transposition table
            self.transposition_table[state_key] = best_score
            return best_score
        
        else:
            best_score = float('+inf')
            opponent = game.get_opponent(player)

            for move in ordered_moves:
                temp_game = game.clone()
                temp_game.make_move(move, opponent)
                score = self.alphabeta(temp_game, depth-1, True, player, alpha, beta, ply+1)
                best_score = min(score, best_score)
                beta = min(beta, best_score)
                
                # If this move caused a cutoff, it's a potential killer move
                if beta <= alpha:
                    self.record_killer_move(move, ply)
                    self.pruning_count += 1
                    break
                
                # Update history heuristic for opponent's good moves
                if score < beta:
                    self.history_table[move] = self.history_table.get(move, 0) + (2 ** depth)
            
            # Store the result in the transposition table
            self.transposition_table[state_key] = best_score
            return best_score

    def order_moves(self, game, valid_moves, player, depth):
        """
        Order moves for better alpha-beta pruning
        1. Captures ordered by MVV-LVA (Most Valuable Victim - Least Valuable Aggressor)
        2. Killer moves
        3. History heuristic
        4. Remaining moves
        """
        # Check if we're dealing with Connect4 moves (integers) or Chess moves (tuples)
        if valid_moves and isinstance(valid_moves[0], int):
            # Connect4 game - moves are column numbers (integers)
            # Simple heuristic: prefer center columns
            board_width = len(game.get_board()[0]) if hasattr(game, 'get_board') else 7
            center = board_width // 2
            
            # Rate moves based on proximity to center
            move_scores = [(move, -abs(move - center)) for move in valid_moves]
            
            # Sort moves by their scores (higher score first)
            move_scores.sort(key=lambda x: x[1], reverse=True)
            ordered_moves = [move for move, _ in move_scores]
            return ordered_moves
        else:
            # Chess game - moves are tuples
            move_scores = []
            
            # Define piece values if not defined elsewhere
            piece_values = {1: 1, 2: 3, 3: 3, 4: 5, 5: 9, 6: 100}
            
            for move in valid_moves:
                from_pos, to_pos = move
                from_row, from_col = from_pos
                to_row, to_col = to_pos
                
                moving_piece = abs(game.board[from_row][from_col])
                target_piece = abs(game.board[to_row][to_col])
                
                score = 0
                # 1. Captures (MVV-LVA)
                if target_piece > 0:  # If it's a capture
                    # Most Valuable Victim (target) - Least Valuable Aggressor (moving piece)
                    score += 10000 + piece_values[target_piece] * 100 - piece_values[moving_piece]
                
                # 2. Killer moves
                if move in self.killer_moves[depth]:
                    score += 9000
                
                # 3. History heuristic
                score += self.history_table.get(move, 0)
                
                move_scores.append((move, score))
            
            # Sort by score in descending order
            return [move for move, score in sorted(move_scores, key=lambda x: x[1], reverse=True)]

    def record_killer_move(self, move, ply):
        """Record a killer move at the current ply"""
        if ply < len(self.killer_moves):
            if move != self.killer_moves[ply][0]:
                self.killer_moves[ply][1] = self.killer_moves[ply][0]
                self.killer_moves[ply][0] = move

    def print_type(self):
        print("alphabeta")