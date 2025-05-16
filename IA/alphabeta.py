from copy import deepcopy
from random import randint

class Alphabeta:
    def __init__(self, max_depth):
        self.max_depth = max_depth

    def get_move(self, game, player):        
        valid_moves = game.get_valid_moves()
        best_move = None
        best_score = float('-inf')
        alpha = float('-inf')
        beta = float('+inf')

        for move in valid_moves:
            temp_game = game.clone()
            temp_game.make_move(move, player)
            score = self.alphabeta(temp_game, self.max_depth, False, player, alpha, beta)
            
            if score >= best_score:
                if score == best_score:
                    # Add randomness to equal-score moves
                    if randint(0,5) == 0:
                        best_move = move
                else:
                    best_score = score
                    alpha = score
                    best_move = move
                    
        if best_move is None:
            if not valid_moves:
                return -1  # Game over
            return valid_moves[0]  # Choose first available move
        return best_move         

    def alphabeta(self, game, depth, tour_max, player, alpha, beta):
        if depth == 0 or game.is_terminal():
            return game.evaluate(player)

        valid_moves = game.get_valid_moves()
        
        if tour_max:
            best_score = float('-inf')
            
            for move in valid_moves:
                temp_game = game.clone()
                temp_game.make_move(move, player)
                score = self.alphabeta(temp_game, depth-1, False, player, alpha, beta)
                best_score = max(score, best_score)
                alpha = max(alpha, best_score)
                
                if beta <= alpha:
                    break
            
            return best_score
        
        else:
            best_score = float('+inf')
            opponent = game.get_opponent(player)

            for move in valid_moves:
                temp_game = game.clone()
                temp_game.make_move(move, opponent)
                score = self.alphabeta(temp_game, depth-1, True, player, alpha, beta)
                best_score = min(score, best_score)
                beta = min(beta, best_score)
                
                if beta <= alpha:
                    break

            return best_score

    def print_type(self):
        print("alphabeta")