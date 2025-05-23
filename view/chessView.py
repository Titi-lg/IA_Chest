import tkinter as tk
from game.chess_game import ChessGame, WHITE, BLACK

# À ADAPTER selon l’IA que tu veux (et son emplacement dans ton projet)
from IA.minimax import Minimax
# from IA.alphabeta import Alphabeta
# from IA.mcts import MCTS

PIECE_UNICODE = {
    1: "♙", -1: "♟",
    2: "♘", -2: "♞",
    3: "♗", -3: "♝",
    5: "♖", -5: "♜",
    9: "♕", -9: "♛",
    100: "♔", -100: "♚"
}

class ChessGUI:
    def __init__(self, root, ai_player=BLACK, ai_algo=None):
        self.root = root
        self.root.title("Chess Game")
        self.size = 60  # taille d’une case
        self.canvas = tk.Canvas(root, width=self.size*8, height=self.size*8)
        self.canvas.pack()
        self.chess_game = ChessGame()
        self.selected = None
        self.valid_moves = []
        self.current_player = WHITE
        self.ai_player = ai_player
        self.ai_algo = ai_algo

        self.draw_board()
        self.draw_pieces()
        self.canvas.bind("<Button-1>", self.on_click)

        # L’IA joue si c’est à elle de commencer :
        self.root.after(100, self.play_ai_if_needed)

    def draw_board(self):
        self.canvas.delete("square")
        for row in range(8):
            for col in range(8):
                color = "#F0D9B5" if (row + col) % 2 == 0 else "#B58863"
                x1 = col * self.size
                y1 = (7 - row) * self.size
                x2 = x1 + self.size
                y2 = y1 + self.size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, tags="square")
        self.canvas.tag_lower("square")

    def draw_pieces(self):
        self.canvas.delete("piece")
        self.canvas.delete("highlight")
        board = self.chess_game.get_board()
        for row in range(8):
            for col in range(8):
                piece = board[row][col]
                if piece != 0:
                    x = col * self.size + self.size // 2
                    y = (7 - row) * self.size + self.size // 2
                    self.canvas.create_text(
                        x, y,
                        text=PIECE_UNICODE.get(piece, "?"),
                        font=("Arial", int(self.size/1.6)),
                        tags="piece"
                    )
        if self.selected:
            self.highlight_square(*self.selected, color="orange")
            for move in self.valid_moves:
                _, to_pos = move
                self.highlight_square(*to_pos, color="yellow")

    def highlight_square(self, row, col, color="yellow"):
        x1 = col * self.size
        y1 = (7 - row) * self.size
        x2 = x1 + self.size
        y2 = y1 + self.size
        self.canvas.create_rectangle(x1, y1, x2, y2, outline=color, width=3, tags="highlight")

    def on_click(self, event):
        # On ignore les clics si c’est à l’IA de jouer
        if self.current_player == self.ai_player:
            return

        col = event.x // self.size
        row = 7 - (event.y // self.size)
        if self.selected is None:
            piece = self.chess_game.get_board()[row][col]
            if (self.current_player == WHITE and piece > 0) or (self.current_player == BLACK and piece < 0):
                self.selected = (row, col)
                self.valid_moves = [move for move in self.chess_game.get_valid_moves() if move[0] == (row, col)]
                self.draw_board()
                self.draw_pieces()
        else:
            move = (self.selected, (row, col))
            if move in self.valid_moves:
                self.chess_game.make_move(move, self.current_player)

                # -- Check roi disparu --
                board = self.chess_game.get_board()
                white_king_present = any(100 == board[r][c] for r in range(8) for c in range(8))
                black_king_present = any(-100 == board[r][c] for r in range(8) for c in range(8))
                if not white_king_present:
                    self.draw_board(); self.draw_pieces()
                    self.end_game("Victoire des Noirs : le roi blanc a disparu."); return
                if not black_king_present:
                    self.draw_board(); self.draw_pieces()
                    self.end_game("Victoire des Blancs : le roi noir a disparu."); return

                if self.chess_game.check_win(self.current_player):
                    self.draw_board(); self.draw_pieces()
                    self.end_game(f"Le joueur {'Blanc' if self.current_player==WHITE else 'Noir'} gagne !")
                    return

                self.current_player = self.chess_game.get_opponent(self.current_player)
            self.selected = None
            self.valid_moves = []
            self.draw_board()
            self.draw_pieces()
            if self.chess_game.is_terminal():
                self.end_game("Match nul ou blocage.")

            # Tour IA ?
            self.root.after(100, self.play_ai_if_needed)

    def play_ai_if_needed(self):
        if self.current_player == self.ai_player and self.ai_algo is not None:
            move = self.ai_algo.get_move(self.chess_game, self.ai_player)
            if move == -1 or move is None:
                self.end_game("L’IA abandonne.")
                return
            self.chess_game.make_move(move, self.current_player)

            board = self.chess_game.get_board()
            white_king_present = any(100 == board[r][c] for r in range(8) for c in range(8))
            black_king_present = any(-100 == board[r][c] for r in range(8) for c in range(8))
            if not white_king_present:
                self.draw_board(); self.draw_pieces()
                self.end_game("Victoire des Noirs : le roi blanc a disparu."); return
            if not black_king_present:
                self.draw_board(); self.draw_pieces()
                self.end_game("Victoire des Blancs : le roi noir a disparu."); return

            if self.chess_game.check_win(self.current_player):
                self.draw_board(); self.draw_pieces()
                self.end_game(f"Le joueur {'Blanc' if self.current_player==WHITE else 'Noir'} gagne !")
                return

            self.current_player = self.chess_game.get_opponent(self.current_player)
            self.selected = None
            self.valid_moves = []
            self.draw_board()
            self.draw_pieces()
            if self.chess_game.is_terminal():
                self.end_game("Match nul ou blocage.")

            # Rejoue IA si c’est encore à elle (pour IA vs IA)
            self.root.after(100, self.play_ai_if_needed)

    def end_game(self, message):
        self.canvas.unbind("<Button-1>")
        self.root.after(300, lambda: tk.messagebox.showinfo("Fin de partie", message))