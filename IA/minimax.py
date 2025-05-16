from copy import deepcopy

class Minimax:
    def __init__(self, max_depth):
        self.max_depth = max_depth

    def get_move(self, game, player):
        valid_moves = game.get_valid_moves()
        best_move = None
        best_score = float('-inf')
        
        for move in valid_moves:
            temp_game = game.clone()
            temp_game.make_move(move, player)
            score = self.minimax(temp_game, self.max_depth, False, player)
            
            if score > best_score:
                best_score = score
                best_move = move   
                
        if best_move is None:
            if not valid_moves:
                return -1  # Game over
            return valid_moves[0]  # Choose first available move
        return best_move         

    def minimax(self, game, depth, tour_max, player):
        if depth == 0 or game.is_terminal():
            return game.evaluate(player)

        valid_moves = game.get_valid_moves()
        
        if tour_max:
            best_score = float('-inf')
            for move in valid_moves:
                temp_game = game.clone()
                temp_game.make_move(move, player)
                score = self.minimax(temp_game, depth-1, False, player)
                best_score = max(score, best_score)
            return best_score
        else:
            best_score = float('+inf')
            opponent = game.get_opponent(player)
            for move in valid_moves:
                temp_game = game.clone()
                temp_game.make_move(move, opponent)
                score = self.minimax(temp_game, depth-1, True, player)
                best_score = min(score, best_score)
            return best_score

    def print_type(self):
        print("minimax")