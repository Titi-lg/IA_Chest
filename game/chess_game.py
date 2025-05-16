from game.abstract_game import AbstractGame
import numpy as np

# Constants for pieces (using standard piece values for evaluation)
EMPTY = 0
PAWN = 1
KNIGHT = 2
BISHOP = 3
ROOK = 5
QUEEN = 9
KING = 100

# Piece colors
WHITE = 1
BLACK = 2

class ChessGame(AbstractGame):
    def __init__(self):
        # Initialize the chess board (8x8)
        # 0 for empty, positive for white pieces, negative for black pieces
        self.board = np.zeros((8, 8), dtype=int)
        self.setup_board()
        self.current_player = WHITE
        self.move_history = []
        
        # Castling rights
        self.white_king_moved = False
        self.black_king_moved = False
        self.white_kingside_rook_moved = False
        self.white_queenside_rook_moved = False
        self.black_kingside_rook_moved = False
        self.black_queenside_rook_moved = False
        
        # En passant target square
        self.en_passant_target = None
        
        # Half-move clock for 50-move rule
        self.halfmove_clock = 0
        
        # Fullmove number
        self.fullmove_number = 1
    
    def setup_board(self):
        """Set up the initial chess position"""
        # Setup pawns
        for col in range(8):
            self.board[1][col] = PAWN  # White pawns
            self.board[6][col] = -PAWN  # Black pawns
        
        # Setup rooks
        self.board[0][0] = self.board[0][7] = ROOK  # White rooks
        self.board[7][0] = self.board[7][7] = -ROOK  # Black rooks
        
        # Setup knights
        self.board[0][1] = self.board[0][6] = KNIGHT  # White knights
        self.board[7][1] = self.board[7][6] = -KNIGHT  # Black knights
        
        # Setup bishops
        self.board[0][2] = self.board[0][5] = BISHOP  # White bishops
        self.board[7][2] = self.board[7][5] = -BISHOP  # Black bishops
        
        # Setup queens
        self.board[0][3] = QUEEN  # White queen
        self.board[7][3] = -QUEEN  # Black queen
        
        # Setup kings
        self.board[0][4] = KING  # White king
        self.board[7][4] = -KING  # Black king
    
    def get_board(self):
        """Returns the current game board"""
        return self.board
    
    def get_valid_moves(self):
        """Returns a list of valid moves in the current state"""
        moves = []
        player = self.current_player
        sign = 1 if player == WHITE else -1
        
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                
                # Skip empty squares and opponent's pieces
                if (player == WHITE and piece <= 0) or (player == BLACK and piece >= 0):
                    continue
                
                # Get piece type (absolute value)
                piece_type = abs(piece)
                
                if piece_type == PAWN:
                    moves.extend(self._get_pawn_moves(row, col, player))
                elif piece_type == KNIGHT:
                    moves.extend(self._get_knight_moves(row, col, player))
                elif piece_type == BISHOP:
                    moves.extend(self._get_bishop_moves(row, col, player))
                elif piece_type == ROOK:
                    moves.extend(self._get_rook_moves(row, col, player))
                elif piece_type == QUEEN:
                    moves.extend(self._get_queen_moves(row, col, player))
                elif piece_type == KING:
                    moves.extend(self._get_king_moves(row, col, player))
                
        # Filter out moves that would leave king in check
        valid_moves = []
        for move in moves:
            temp_game = self.clone()
            temp_game.make_move(move, player)
            if not temp_game._is_in_check(player):
                valid_moves.append(move)
                
        return valid_moves
    
    def _get_pawn_moves(self, row, col, player):
        """Get all valid pawn moves"""
        moves = []
        direction = 1 if player == WHITE else -1
        
        # Forward move
        if 0 <= row + direction < 8 and self.board[row + direction][col] == 0:
            moves.append(((row, col), (row + direction, col)))
            
            # Double forward move from starting position
            if (player == WHITE and row == 1) or (player == BLACK and row == 6):
                if self.board[row + 2 * direction][col] == 0:
                    moves.append(((row, col), (row + 2 * direction, col)))
        
        # Captures
        for c_offset in [-1, 1]:
            if 0 <= col + c_offset < 8 and 0 <= row + direction < 8:
                # Regular capture
                target = self.board[row + direction][col + c_offset]
                if (player == WHITE and target < 0) or (player == BLACK and target > 0):
                    moves.append(((row, col), (row + direction, col + c_offset)))
                
                # En passant capture
                if self.en_passant_target == (row + direction, col + c_offset):
                    moves.append(((row, col), (row + direction, col + c_offset)))
        
        return moves
    
    def _get_knight_moves(self, row, col, player):
        """Get all valid knight moves"""
        moves = []
        offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        
        for r_offset, c_offset in offsets:
            new_row, new_col = row + r_offset, col + c_offset
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = self.board[new_row][new_col]
                if target == 0 or (player == WHITE and target < 0) or (player == BLACK and target > 0):
                    moves.append(((row, col), (new_row, new_col)))
        
        return moves
    
    def _get_bishop_moves(self, row, col, player):
        """Get all valid bishop moves"""
        moves = []
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]  # Diagonals
        
        for r_dir, c_dir in directions:
            for i in range(1, 8):
                new_row, new_col = row + i * r_dir, col + i * c_dir
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                
                target = self.board[new_row][new_col]
                if target == 0:
                    moves.append(((row, col), (new_row, new_col)))
                elif (player == WHITE and target < 0) or (player == BLACK and target > 0):
                    moves.append(((row, col), (new_row, new_col)))
                    break
                else:
                    break
        
        return moves
    
    def _get_rook_moves(self, row, col, player):
        """Get all valid rook moves"""
        moves = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Orthogonals
        
        for r_dir, c_dir in directions:
            for i in range(1, 8):
                new_row, new_col = row + i * r_dir, col + i * c_dir
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                
                target = self.board[new_row][new_col]
                if target == 0:
                    moves.append(((row, col), (new_row, new_col)))
                elif (player == WHITE and target < 0) or (player == BLACK and target > 0):
                    moves.append(((row, col), (new_row, new_col)))
                    break
                else:
                    break
        
        return moves
    
    def _get_queen_moves(self, row, col, player):
        """Get all valid queen moves (combination of bishop and rook)"""
        return self._get_bishop_moves(row, col, player) + self._get_rook_moves(row, col, player)
    
    def _get_king_moves(self, row, col, player):
        """Get all valid king moves"""
        moves = []
        offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        
        # Regular king moves
        for r_offset, c_offset in offsets:
            new_row, new_col = row + r_offset, col + c_offset
            if 0 <= new_row < 8 and 0 <= new_col < 8:
                target = self.board[new_row][new_col]
                if target == 0 or (player == WHITE and target < 0) or (player == BLACK and target > 0):
                    moves.append(((row, col), (new_row, new_col)))
        
        # Castling
        if player == WHITE and not self.white_king_moved and row == 0 and col == 4:
            # Kingside castling
            if not self.white_kingside_rook_moved and all(self.board[0][c] == 0 for c in range(5, 7)):
                if not self._is_square_attacked(0, 4, BLACK) and not self._is_square_attacked(0, 5, BLACK):
                    moves.append(((0, 4), (0, 6)))
            
            # Queenside castling
            if not self.white_queenside_rook_moved and all(self.board[0][c] == 0 for c in range(1, 4)):
                if not self._is_square_attacked(0, 4, BLACK) and not self._is_square_attacked(0, 3, BLACK):
                    moves.append(((0, 4), (0, 2)))
                
        elif player == BLACK and not self.black_king_moved and row == 7 and col == 4:
            # Kingside castling
            if not self.black_kingside_rook_moved and all(self.board[7][c] == 0 for c in range(5, 7)):
                if not self._is_square_attacked(7, 4, WHITE) and not self._is_square_attacked(7, 5, WHITE):
                    moves.append(((7, 4), (7, 6)))
            
            # Queenside castling
            if not self.black_queenside_rook_moved and all(self.board[7][c] == 0 for c in range(1, 4)):
                if not self._is_square_attacked(7, 4, WHITE) and not self._is_square_attacked(7, 3, WHITE):
                    moves.append(((7, 4), (7, 2)))
        
        return moves
    
    def _is_square_attacked(self, row, col, attacker):
        """Check if a square is under attack by the specified player"""
        # This is a simplified version that doesn't handle all edge cases
        sign = 1 if attacker == WHITE else -1
        
        # Check for pawn attacks
        pawn_row = row + (-sign)
        for c_offset in [-1, 1]:
            pawn_col = col + c_offset
            if 0 <= pawn_row < 8 and 0 <= pawn_col < 8:
                if self.board[pawn_row][pawn_col] == sign * PAWN:
                    return True
        
        # Check knight attacks
        knight_offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
        for r_offset, c_offset in knight_offsets:
            new_row, new_col = row + r_offset, col + c_offset
            if 0 <= new_row < 8 and 0 <= new_col < 8 and self.board[new_row][new_col] == sign * KNIGHT:
                return True
        
        # Check diagonal attacks (bishop, queen)
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        for r_dir, c_dir in directions:
            for i in range(1, 8):
                new_row, new_col = row + i * r_dir, col + i * c_dir
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                piece = self.board[new_row][new_col]
                if piece != 0:
                    if piece == sign * BISHOP or piece == sign * QUEEN:
                        return True
                    break
        
        # Check orthogonal attacks (rook, queen)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for r_dir, c_dir in directions:
            for i in range(1, 8):
                new_row, new_col = row + i * r_dir, col + i * c_dir
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                piece = self.board[new_row][new_col]
                if piece != 0:
                    if piece == sign * ROOK or piece == sign * QUEEN:
                        return True
                    break
        
        # Check king attacks
        king_offsets = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for r_offset, c_offset in king_offsets:
            new_row, new_col = row + r_offset, col + c_offset
            if 0 <= new_row < 8 and 0 <= new_col < 8 and self.board[new_row][new_col] == sign * KING:
                return True
        
        return False
    
    def _is_in_check(self, player):
        """Check if the specified player is in check"""
        # Find the king
        king_value = KING if player == WHITE else -KING
        king_pos = None
        for row in range(8):
            for col in range(8):
                if self.board[row][col] == king_value:
                    king_pos = (row, col)
                    break
            if king_pos:
                break
        
        # If no king found, something is wrong
        if not king_pos:
            return False
        
        # Check if king is under attack
        opponent = BLACK if player == WHITE else WHITE
        return self._is_square_attacked(king_pos[0], king_pos[1], opponent)
    
    def make_move(self, move, player):
        """Makes a move on the board for the given player"""
        from_pos, to_pos = move
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Store previous state for en passant detection
        prev_board = np.copy(self.board)
        
        # Reset en passant target
        old_en_passant = self.en_passant_target
        self.en_passant_target = None
        
        # Get the moving piece
        piece = self.board[from_row][from_col]
        abs_piece = abs(piece)
        
        # Check if this is a capture move
        is_capture = self.board[to_row][to_col] != 0
        
        # Update halfmove clock
        if abs_piece == PAWN or is_capture:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1
        
        # Handle special pawn moves
        if abs_piece == PAWN:
            # Double push (set en passant target)
            if abs(from_row - to_row) == 2:
                self.en_passant_target = (from_row + (to_row - from_row) // 2, from_col)
            
            # En passant capture
            elif to_pos == old_en_passant:
                # Remove the captured pawn
                ep_row = to_row - (1 if player == WHITE else -1)
                self.board[ep_row][to_col] = 0
            
            # Promotion (default to queen)
            elif (player == WHITE and to_row == 7) or (player == BLACK and to_row == 0):
                piece = QUEEN if player == WHITE else -QUEEN
        
        # Handle castling
        elif abs_piece == KING:
            # Update king moved status
            if player == WHITE:
                self.white_king_moved = True
            else:
                self.black_king_moved = True
                
            # Kingside castling
            if from_col == 4 and to_col == 6:
                # Move the rook
                self.board[from_row][7] = 0
                self.board[from_row][5] = ROOK if player == WHITE else -ROOK
            
            # Queenside castling
            elif from_col == 4 and to_col == 2:
                # Move the rook
                self.board[from_row][0] = 0
                self.board[from_row][3] = ROOK if player == WHITE else -ROOK
        
        # Handle rook moves for castling rights
        elif abs_piece == ROOK:
            if player == WHITE:
                if from_row == 0 and from_col == 0:
                    self.white_queenside_rook_moved = True
                elif from_row == 0 and from_col == 7:
                    self.white_kingside_rook_moved = True
            else:
                if from_row == 7 and from_col == 0:
                    self.black_queenside_rook_moved = True
                elif from_row == 7 and from_col == 7:
                    self.black_kingside_rook_moved = True
        
        # Move the piece
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = 0
        
        # Update fullmove number
        if player == BLACK:
            self.fullmove_number += 1
        
        # Switch current player
        self.current_player = self.get_opponent(player)
        
        # Record the move
        self.move_history.append(move)
        
        return True
    
    def is_terminal(self):
        """Checks if the game is over"""
        # Check for checkmate or stalemate
        white_moves = len(self._get_moves_for_player(WHITE))
        black_moves = len(self._get_moves_for_player(BLACK))
        
        # No legal moves for current player
        if (self.current_player == WHITE and white_moves == 0) or \
           (self.current_player == BLACK and black_moves == 0):
            return True
        
        # 50-move rule
        if self.halfmove_clock >= 100:  # 50 full moves
            return True
        
        # Insufficient material (simplified)
        remaining_pieces = [abs(self.board[r][c]) for r in range(8) for c in range(8) if self.board[r][c] != 0]
        if len(remaining_pieces) <= 2:  # Just kings
            return True
        if len(remaining_pieces) == 3 and (KNIGHT in remaining_pieces or BISHOP in remaining_pieces):
            # King + King + Bishop/Knight
            return True
        
        return False
    
    def _get_moves_for_player(self, player):
        """Get all legal moves for a specific player"""
        # Save current player
        current = self.current_player
        # Set requested player
        self.current_player = player
        # Get moves
        moves = self.get_valid_moves()
        # Restore current player
        self.current_player = current
        return moves
    
    def evaluate(self, player):
        """Evaluates the board for the given player"""
        if self.is_terminal():
            # Check for checkmate
            opponent = self.get_opponent(player)
            if self._is_in_check(opponent) and len(self._get_moves_for_player(opponent)) == 0:
                return float('inf')  # Player wins
            elif self._is_in_check(player) and len(self._get_moves_for_player(player)) == 0:
                return float('-inf')  # Player loses
            else:
                return 0  # Draw
        
        # Material evaluation
        white_material = 0
        black_material = 0
        
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece > 0:
                    white_material += abs(piece)
                elif piece < 0:
                    black_material += abs(piece)
        
        # Position evaluation (simplified)
        white_position = self._evaluate_position(WHITE)
        black_position = self._evaluate_position(BLACK)
        
        # Combine material and position evaluations
        white_score = white_material + white_position
        black_score = black_material + black_position
        
        if player == WHITE:
            return white_score - black_score
        else:
            return black_score - white_score
    
    def _evaluate_position(self, player):
        """Simple positional evaluation"""
        score = 0
        sign = 1 if player == WHITE else -1
        
        # Control of center
        center_squares = [(3, 3), (3, 4), (4, 3), (4, 4)]
        for row, col in center_squares:
            piece = self.board[row][col]
            if piece * sign > 0:  # Player's piece
                score += 0.5
        
        # Development in opening
        if len(self.move_history) < 20:  # Early game
            # Knights and bishops out
            if player == WHITE:
                if self.board[0][1] == 0:  # Knight moved
                    score += 0.3
                if self.board[0][6] == 0:  # Knight moved
                    score += 0.3
                if self.board[0][2] == 0:  # Bishop moved
                    score += 0.3
                if self.board[0][5] == 0:  # Bishop moved
                    score += 0.3
            else:
                if self.board[7][1] == 0:  # Knight moved
                    score += 0.3
                if self.board[7][6] == 0:  # Knight moved
                    score += 0.3
                if self.board[7][2] == 0:  # Bishop moved
                    score += 0.3
                if self.board[7][5] == 0:  # Bishop moved
                    score += 0.3
        
        return score
    
    def check_win(self, player):
        """Checks if the specified player has won"""
        opponent = self.get_opponent(player)
        return self._is_in_check(opponent) and len(self._get_moves_for_player(opponent)) == 0
    
    def get_opponent(self, player):
        """Returns the opponent of the given player"""
        return BLACK if player == WHITE else WHITE
