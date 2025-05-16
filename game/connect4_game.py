from game.abstract_game import AbstractGame

EMPTY = 0
PLAYER1 = 1
PLAYER2 = 2
ROW_COUNT = 6
COLUMN_COUNT = 7

class Connect4Game(AbstractGame):
    def __init__(self):
        # Initialize an empty Connect4 board
        self.board = [[EMPTY for _ in range(COLUMN_COUNT)] for _ in range(ROW_COUNT)]
        self.game_over = False
        
    def get_board(self):
        return self.board
        
    def get_valid_moves(self):
        valid_moves = []
        # Prioritize center and nearby columns for better gameplay
        if self.board[ROW_COUNT-1][3] == EMPTY:
            valid_moves.append(3)
        if self.board[ROW_COUNT-1][2] == EMPTY:
            valid_moves.append(2)
        if self.board[ROW_COUNT-1][4] == EMPTY:
            valid_moves.append(4)
        if self.board[ROW_COUNT-1][1] == EMPTY:
            valid_moves.append(1)
        if self.board[ROW_COUNT-1][5] == EMPTY:
            valid_moves.append(5)
        if self.board[ROW_COUNT-1][0] == EMPTY:
            valid_moves.append(0)
        if self.board[ROW_COUNT-1][6] == EMPTY:
            valid_moves.append(6)
        return valid_moves
    
    def make_move(self, move, player):
        row = self._get_next_open_row(move)
        if row >= 0:
            self.board[row][move] = player
            return True
        return False
    
    def _get_next_open_row(self, col):
        for row in range(ROW_COUNT):
            if self.board[row][col] == EMPTY:
                return row
        return -1
        
    def is_terminal(self):
        return self.check_win(1) or self.check_win(2) or len(self.get_valid_moves()) == 0
    
    def check_win(self, player):
        # Check horizontal
        for row in range(ROW_COUNT):
            for col in range(COLUMN_COUNT-3):
                if all(self.board[row][col+i] == player for i in range(4)):
                    return True
        
        # Check vertical
        for row in range(ROW_COUNT-3):
            for col in range(COLUMN_COUNT):
                if all(self.board[row+i][col] == player for i in range(4)):
                    return True
        
        # Check diagonal (positive slope)
        for row in range(ROW_COUNT-3):
            for col in range(COLUMN_COUNT-3):
                if all(self.board[row+i][col+i] == player for i in range(4)):
                    return True
        
        # Check diagonal (negative slope)
        for row in range(3, ROW_COUNT):
            for col in range(COLUMN_COUNT-3):
                if all(self.board[row-i][col+i] == player for i in range(4)):
                    return True
        return False
    
    def get_opponent(self, player):
        return 3 - player
    
    def evaluate(self, player):
        score = 0
        # Horizontal evaluation
        for r in range(ROW_COUNT):
            row_array = [int(i) for i in list(self.board[r])]
            for c in range(COLUMN_COUNT - 3):
                window = row_array[c:c+4]
                score += self._evaluate_window(window, player)

        # Vertical evaluation
        for c in range(COLUMN_COUNT):
            col_array = [self.board[i][c] for i in range(ROW_COUNT)]
            for r in range(ROW_COUNT - 3):
                window = col_array[r:r+4]
                score += self._evaluate_window(window, player)        

        # Positive diagonal evaluation
        for r in range(ROW_COUNT - 3):
            for c in range(COLUMN_COUNT - 3):
                window = [self.board[r+i][c+i] for i in range(4)]
                score += self._evaluate_window(window, player)

        # Negative diagonal evaluation
        for r in range(3, ROW_COUNT):
            for c in range(COLUMN_COUNT - 3):
                window = [self.board[r-i][c+i] for i in range(4)]
                score += self._evaluate_window(window, player)        
        
        return score
    
    def _evaluate_window(self, window, player):
        opp_player = self.get_opponent(player)
        
        if window.count(EMPTY) > 2:
            return 0
        if window.count(player) > 0 and window.count(opp_player) > 0:
            return 0
        
        if window.count(EMPTY) == 2:
            if window.count(player) == 2:
                return 15
            else:
                return -15
        if window.count(EMPTY) == 1:
            if window.count(player) == 3:
                return 50
            else:
                return -50
            
        if window.count(player) == 4:
            return float('inf')
        if window.count(opp_player) == 4:
            return float('-inf')
            
        return 0
