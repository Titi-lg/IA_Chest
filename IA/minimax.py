from copy import deepcopy

class Minimax:
    def __init__(self, max_depth):
        self.max_depth = max_depth
        # Add a transposition table to cache positions
        self.transposition_table = {}
        # Add history table for move ordering
        self.history_table = {}
        # Stats for optimization monitoring
        self.nodes_evaluated = 0
        self.tt_hits = 0

    def get_move(self, game, player):
        valid_moves = game.get_valid_moves()
        best_move = None
        best_score = float('-inf')
        
        # Clear the tables for a new search
        self.transposition_table = {}
        self.history_table = {}
        self.nodes_evaluated = 0
        self.tt_hits = 0
        
        # Order moves for initial search
        ordered_moves = self.order_moves(game, valid_moves, player)
        
        for move in ordered_moves:
            temp_game = game.clone()
            temp_game.make_move(move, player)
            score = self.minimax(temp_game, self.max_depth, False, player)
            
            if score > best_score:
                best_score = score
                best_move = move
            
            # Remember good moves
            self.history_table[move] = self.history_table.get(move, 0) + (2 ** self.max_depth)
                
        if best_move is None:
            if not valid_moves:
                return -1  # Game over
            return valid_moves[0]  # Choose first available move
            
        # Print statistics if requested
        # print(f"Nodes evaluated: {self.nodes_evaluated}, TT hits: {self.tt_hits}")
        
        return best_move         

    def minimax(self, game, depth, tour_max, player):
        self.nodes_evaluated += 1
        
        if depth == 0 or game.is_terminal():
            return game.evaluate(player)
        
        # Create a hash key for the current position - handle different board types
        if hasattr(game.board, 'tobytes'):
            # For numpy arrays
            board_hash = str(game.board.tobytes())
        elif isinstance(game.board, list):
            # For list-based boards
            board_hash = str(game.board)
        else:
            # Fallback for any other type
            board_hash = str(game.board)
            
        state_key = (board_hash, depth, tour_max, player)
        
        # Check if position is in transposition table
        if state_key in self.transposition_table:
            self.tt_hits += 1
            return self.transposition_table[state_key]
            
        valid_moves = game.get_valid_moves()
        
        # Order moves for better performance
        if tour_max:
            current_player = player
        else:
            current_player = game.get_opponent(player)
            
        ordered_moves = self.order_moves(game, valid_moves, current_player)
        
        if tour_max:
            best_score = float('-inf')
            for move in ordered_moves:
                temp_game = game.clone()
                temp_game.make_move(move, player)
                score = self.minimax(temp_game, depth-1, False, player)
                best_score = max(score, best_score)
                
                # Update history heuristic
                if score > best_score - 0.5:  # If good move
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
                score = self.minimax(temp_game, depth-1, True, player)
                best_score = min(score, best_score)
                
                # Update history heuristic for opponent
                if score < best_score + 0.5:  # If good move for opponent
                    self.history_table[move] = self.history_table.get(move, 0) + (2 ** depth)
            
            # Store the result in the transposition table
            self.transposition_table[state_key] = best_score
            return best_score
    
    def order_moves(self, game, valid_moves, player):
        """Order moves based on simple heuristics to improve pruning."""
        # For Connect4, moves are integers (column numbers)
        # For Chess, moves are tuples (from_pos, to_pos)
        
        if hasattr(game, 'name') and game.name == 'Connect4':
            # Connect4 specific move ordering
            # Prioritize center columns
            center = game.cols // 2
            return sorted(valid_moves, key=lambda move: abs(move - center))
        else:
            # Chess specific move ordering
            scored_moves = []
            for move in valid_moves:
                score = 0
                # Check if we're dealing with a tuple move (chess-like)
                if isinstance(move, tuple) and len(move) == 2:
                    from_pos, to_pos = move
                    # Add your chess-specific ordering logic here
                    # ...existing chess ordering logic...
                else:
                    # Fallback for other move types
                    score = 0
                scored_moves.append((move, score))
            
            # Sort moves by score in descending order
            scored_moves.sort(key=lambda x: x[1], reverse=True)
            return [move for move, _ in scored_moves]

    def print_type(self):
        print("minimax")