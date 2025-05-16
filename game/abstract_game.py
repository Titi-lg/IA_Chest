from abc import ABC, abstractmethod
from copy import deepcopy

class AbstractGame(ABC):
    @abstractmethod
    def get_board(self):
        """Returns the current game board"""
        pass
    
    @abstractmethod
    def get_valid_moves(self):
        """Returns a list of valid moves in the current state"""
        pass
    
    @abstractmethod
    def make_move(self, move, player):
        """Makes a move on the board for the given player"""
        pass
    
    @abstractmethod
    def is_terminal(self):
        """Checks if the game is over"""
        pass
    
    @abstractmethod
    def evaluate(self, player):
        """Evaluates the board for the given player"""
        pass
    
    @abstractmethod
    def check_win(self, player):
        """Checks if the specified player has won"""
        pass
    
    @abstractmethod
    def get_opponent(self, player):
        """Returns the opponent of the given player"""
        pass
    
    def clone(self):
        """Returns a deep copy of the game"""
        return deepcopy(self)
