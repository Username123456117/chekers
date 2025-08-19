import tkinter as tk
import random

# Constants
ROWS, COLS = 8, 8
SQUARE_SIZE = 60

# Colors
LIGHT_SQUARE = "#EEEED2"
DARK_SQUARE = "#769656"
RED_PIECE = "#FF0000"
BLACK_PIECE = "#000000"
KING_OUTLINE = "#FFD700"  # gold outline for kings

class Checkers:
    def __init__(self, root, mode="AI", difficulty="Easy",
                 mandatory_jump=True, move_after_touch=True):
        self.root = root
        self.mode = mode
        self.difficulty = difficulty
        self.mandatory_jump = mandatory_jump
        self.move_after_touch = move_after_touch

        self.root.title("Checkers")
        self.turn = 'red'
        self.selected_piece = None
        self.board = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.piece_info = {}  # Track color and king status
        self.canvas = tk.Canvas(root, width=COLS*SQUARE_SIZE, height=ROWS*SQUARE_SIZE)
        self.canvas.pack()
        self.draw_board()
        self.place_pieces()
        self.canvas.bind("<Button-1>", self.click)

    def draw_board(self):
        for row in range(ROWS):
            for col in range(COLS):
                color = LIGHT_SQUARE if (row+col) % 2 == 0 else DARK_SQUARE
                self.canvas.create_rectangle(col*SQUARE_SIZE, row*SQUARE_SIZE,
                                             (col+1)*SQUARE_SIZE, (row+1)*SQUARE_SIZE,
                                             fill=color)

    def place_pieces(self):
        for row in range(ROWS):
            for col in range(COLS):
                if (row+col) % 2 != 0:
                    if row < 3:
                        self.create_piece(row, col, BLACK_PIECE)
                    elif row > 4:
                        self.create_piece(row, col, RED_PIECE)

    def create_piece(self, row, col, color):
        x1 = col * SQUARE_SIZE + 10
        y1 = row * SQUARE_SIZE + 10
        x2 = x1 + SQUARE_SIZE - 20
        y2 = y1 + SQUARE_SIZE - 20
        piece = self.canvas.create_oval(x1, y1, x2, y2, fill=color, width=2)
        self.board[row][col] = piece
        self.piece_info[piece] = {"color": color, "king": False}

    def click(self, event):
        col = event.x // SQUARE_SIZE
        row = event.y // SQUARE_SIZE
        piece = self.board[row][col]

        # Determine pieces that must jump if mandatory jump is on
        jump_pieces = []
        if self.mandatory_jump:
            for r in range(ROWS):
                for c in range(COLS):
                    p = self.board[r][c]
                    if p and self.piece_info[p]["color"] == (RED_PIECE if self.turn=="red" else BLACK_PIECE):
                        if self.can_jump(r, c):
                            jump_pieces.append((r, c))

        if piece:
            info = self.piece_info[piece]
            if info["color"] == (RED_PIECE if self.turn=="red" else BLACK_PIECE):
                if self.mandatory_jump and jump_pieces and (row, col) not in jump_pieces:
                    return  # Must select a piece that can jump
                if self.move_after_touch:
                    if self.selected_piece == (row, col):
                        self.selected_piece = None
                    elif self.selected_piece is None:
                        self.selected_piece = (row, col)
                else:
                    self.selected_piece = (row, col)
        elif self.selected_piece:
            self.move_piece(row, col)

    def move_piece(self, row, col):
        src_row, src_col = self.selected_piece
        piece = self.board[src_row][src_col]
        info = self.piece_info[piece]

        if self.valid_move(src_row, src_col, row, col):
            dr = row - src_row
            dc = col - src_col

            # Jump capture
            if abs(dr) == 2 and abs(dc) == 2:
                mid_row = src_row + dr // 2
                mid_col = src_col + dc // 2
                captured_piece = self.board[mid_row][mid_col]
                self.canvas.delete(captured_piece)
                self.board[mid_row][mid_col] = None
                del self.piece_info[captured_piece]

            # Move piece
            self.canvas.move(piece, dc*SQUARE_SIZE, dr*SQUARE_SIZE)
            self.board[row][col] = piece
            self.board[src_row][src_col] = None

            # Promote to king
            if info["color"] == RED_PIECE and row == 0:
                info["king"] = True
                self.canvas.itemconfig(piece, outline=KING_OUTLINE, width=3)
            elif info["color"] == BLACK_PIECE and row == ROWS-1:
                info["king"] = True
                self.canvas.itemconfig(piece, outline=KING_OUTLINE, width=3)

            # Chain jumps
            if abs(dr) == 2 and self.can_jump(row, col):
                self.selected_piece = (row, col)
            else:
                self.selected_piece = None
                self.turn = 'black' if self.turn == 'red' else 'red'
                if self.mode == "AI" and self.turn == 'black':
                    self.root.after(500, self.ai_move)
            return True
        return False

    def valid_move(self, src_row, src_col, dest_row, dest_col):
        if self.board[dest_row][dest_col] is not None:
            return False
        dr = dest_row - src_row
        dc = dest_col - src_col
        piece = self.board[src_row][src_col]
        info = self.piece_info[piece]
        color = info["color"]
        king = info["king"]

        # Normal move
        if abs(dr) == 1 and abs(dc) == 1:
            if king:
                return True
            if color == RED_PIECE and dr == -1:
                return True
            if color == BLACK_PIECE and dr == 1:
                return True
            return False

        # Jump move
        if abs(dr) == 2 and abs(dc) == 2:
            mid_row = src_row + dr//2
            mid_col = src_col + dc//2
            mid_piece = self.board[mid_row][mid_col]
            if mid_piece is None:
                return False
            mid_color = self.piece_info[mid_piece]["color"]
            if color == RED_PIECE and mid_color == BLACK_PIECE:
                return True
            if color == BLACK_PIECE and mid_color == RED_PIECE:
                return True
            if king and ((color == RED_PIECE and mid_color == BLACK_PIECE) or
                         (color == BLACK_PIECE and mid_color == RED_PIECE)):
                return True
        return False

    def can_jump(self, row, col):
        piece = self.board[row][col]
        info = self.piece_info[piece]
        directions = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS:
                if self.valid_move(row, col, nr, nc):
                    return True
        return False

    # AI
    def ai_move(self):
        black_pieces = [ (r,c) for r in range(ROWS) for c in range(COLS)
                         if self.board[r][c] and self.piece_info[self.board[r][c]]["color"]==BLACK_PIECE ]

        jump_pieces = [p for p in black_pieces if self.can_jump(p[0], p[1])]
        if self.mandatory_jump and jump_pieces:
            black_pieces = jump_pieces

        if self.difficulty == "Easy":
            self.ai_random_move(black_pieces)
        elif self.difficulty == "Medium":
            self.ai_medium(black_pieces)
        elif self.difficulty == "Adaptive":
            self.ai_adaptive(black_pieces)
        elif self.difficulty == "Hard":
            self.ai_hard(black_pieces)
        self.turn = 'red'

    def ai_random_move(self, black_pieces):
        random.shuffle(black_pieces)
        for r, c in black_pieces:
            for dr, dc in [(-2,-2), (-2,2), (2,-2), (2,2), (-1,-1), (-1,1), (1,-1), (1,1)]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < ROWS and 0 <= nc < COLS and self.valid_move(r,c,nr,nc):
                    self.selected_piece = (r,c)
                    self.move_piece(nr,nc)
                    return

    def ai_medium(self, black_pieces):
        moves = []
        for r, c in black_pieces:
            for dr, dc in [(-2,-2), (-2,2), (2,-2), (2,2), (-1,-1), (-1,1), (1,-1), (1,1)]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < ROWS and 0 <= nc < COLS and self.valid_move(r,c,nr,nc):
                    score = 2 if abs(dr)==2 else 1
                    moves.append((score, r,c,nr,nc))
        if moves:
            moves.sort(reverse=True)
            _, r,c,nr,nc = moves[0]
            self.selected_piece = (r,c)
            self.move_piece(nr,nc)

    def count_threats(self, row, col):
        threats = 0
        for dr, dc in [(-1,-1), (-1,1), (1,-1), (1,1)]:
            r2, c2 = row + dr*2, col + dc*2
            r1, c1 = row + dr, col + dc
            if 0 <= r2 < ROWS and 0 <= c2 < COLS:
                mid_piece = self.board[r1][c1]
                dest_piece = self.board[r2][c2]
                if mid_piece and self.piece_info[mid_piece]["color"]==RED_PIECE and dest_piece is None:
                    threats += 1
        return threats

    def ai_adaptive(self, black_pieces):
        moves = []
        for r,c in black_pieces:
            for dr, dc in [(-2,-2), (-2,2), (2,-2), (2,2), (-1,-1), (-1,1), (1,-1), (1,1)]:
                nr, nc = r+dr, c+dc
                if 0<=nr<ROWS and 0<=nc<COLS and self.valid_move(r,c,nr,nc):
                    danger = self.count_threats(nr,nc)
                    score = 2 if abs(dr)==2 else 1
                    moves.append((score-danger,r,c,nr,nc))
        if moves:
            moves.sort(reverse=True)
            _, r,c,nr,nc = moves[0]
            self.selected_piece = (r,c)
            self.move_piece(nr,nc)

    def evaluate_move(self, r,c,nr,nc):
        score = 0
        if abs(nr-r)==2:
            score += 2
        score -= self.count_threats(nr,nc)
        return score

    def ai_hard(self, black_pieces):
        best_move = None
        best_score = -float('inf')
        for r,c in black_pieces:
            for dr,dc in [(-2,-2),(-2,2),(2,-2),(2,2),(-1,-1),(-1,1),(1,-1),(1,1)]:
                nr,nc = r+dr, c+dc
                if 0<=nr<ROWS and 0<=nc<COLS and self.valid_move(r,c,nr,nc):
                    score = self.evaluate_move(r,c,nr,nc)
                    if score > best_score:
                        best_score = score
                        best_move = (r,c,nr,nc)
        if best_move:
            r,c,nr,nc = best_move
            self.selected_piece = (r,c)
            self.move_piece(nr,nc)


def rule_menu():
    root = tk.Tk()
    root.title("Checkers Rules")
    root.geometry("400x380")

    mode_var = tk.StringVar(value="AI")
    difficulty_var = tk.StringVar(value="Easy")
    mandatory_jump_var = tk.BooleanVar(value=True)
    move_after_touch_var = tk.BooleanVar(value=True)

    def start_game():
        root.destroy()
        game_root = tk.Tk()
        Checkers(game_root,
                 mode=mode_var.get(),
                 difficulty=difficulty_var.get(),
                 mandatory_jump=mandatory_jump_var.get(),
                 move_after_touch=move_after_touch_var.get())
        game_root.mainloop()

    tk.Label(root, text="Select Game Mode", font=("Arial", 16)).pack(pady=5)
    tk.Radiobutton(root, text="Play vs AI", variable=mode_var, value="AI").pack()
    tk.Radiobutton(root, text="2 Player", variable=mode_var, value="2P").pack()

    tk.Label(root, text="AI Difficulty", font=("Arial", 16)).pack(pady=5)
    tk.Radiobutton(root, text="Easy", variable=difficulty_var, value="Easy").pack()
    tk.Radiobutton(root, text="Medium", variable=difficulty_var, value="Medium").pack()
    tk.Radiobutton(root, text="Adaptive", variable=difficulty_var, value="Adaptive").pack()
    tk.Radiobutton(root, text="Hard", variable=difficulty_var, value="Hard").pack()

    tk.Label(root, text="Rules", font=("Arial", 16)).pack(pady=5)
    tk.Checkbutton(root, text="Mandatory Jumps", variable=mandatory_jump_var).pack()
    tk.Checkbutton(root, text="Move After Touch", variable=move_after_touch_var).pack()

    tk.Button(root, text="Start Game", command=start_game, width=20).pack(pady=10)
    root.mainloop()

if __name__ == "__main__":
    rule_menu()
