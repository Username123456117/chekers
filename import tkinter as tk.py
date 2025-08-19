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

class Checkers:
    def __init__(self, root, mode="AI", mandatory_jump=True, move_after_touch=True):
        self.root = root
        self.mode = mode  # "AI" or "2P"
        self.mandatory_jump = mandatory_jump
        self.move_after_touch = move_after_touch

        self.root.title("Checkers")
        self.turn = 'red'
        self.selected_piece = None
        self.board = [[None for _ in range(COLS)] for _ in range(ROWS)]
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
        piece = self.canvas.create_oval(x1, y1, x2, y2, fill=color)
        self.board[row][col] = piece

    def click(self, event):
        col = event.x // SQUARE_SIZE
        row = event.y // SQUARE_SIZE
        piece = self.board[row][col]

        # Mandatory jump: find all pieces that can jump
        jump_pieces = []
        if self.mandatory_jump:
            for r in range(ROWS):
                for c in range(COLS):
                    p = self.board[r][c]
                    if p:
                        color = self.canvas.itemcget(p, "fill")
                        if ((self.turn == "red" and color == RED_PIECE) or
                            (self.turn == "black" and color == BLACK_PIECE)):
                            if self.can_jump(r, c):
                                jump_pieces.append((r, c))

        # Selecting a piece
        if piece:
            piece_color = self.canvas.itemcget(piece, "fill")
            if ((self.turn == 'red' and piece_color == RED_PIECE) or
                (self.mode == "2P" and self.turn == 'black' and piece_color == BLACK_PIECE)):

                # If mandatory jump, only allow selecting a jumping piece
                if self.mandatory_jump and jump_pieces and (row, col) not in jump_pieces:
                    return

                # Move after touch: deselect only if clicking same piece again
                if self.move_after_touch:
                    if self.selected_piece == (row, col):
                        self.selected_piece = None
                    elif self.selected_piece is None:
                        self.selected_piece = (row, col)
                else:
                    self.selected_piece = (row, col)

        # Move piece if selected
        elif self.selected_piece:
            self.move_piece(row, col)

    def move_piece(self, row, col):
        src_row, src_col = self.selected_piece
        piece = self.board[src_row][src_col]

        if self.valid_move(src_row, src_col, row, col):
            dr = row - src_row
            dc = col - src_col

            # Check for jump
            if abs(dr) == 2 and abs(dc) == 2:
                mid_row = src_row + dr // 2
                mid_col = src_col + dc // 2
                captured_piece = self.board[mid_row][mid_col]
                self.canvas.delete(captured_piece)
                self.board[mid_row][mid_col] = None

            # Move piece
            self.canvas.move(piece, dc*SQUARE_SIZE, dr*SQUARE_SIZE)
            self.board[row][col] = piece
            self.board[src_row][src_col] = None

            # Check for additional jumps
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
        piece_color = self.canvas.itemcget(self.board[src_row][src_col], "fill")

        # Simple diagonal move
        if abs(dr) == 1 and abs(dc) == 1:
            if piece_color == RED_PIECE and dr == -1:
                return True
            if piece_color == BLACK_PIECE and dr == 1:
                return True
            return False

        # Jump over opponent
        if abs(dr) == 2 and abs(dc) == 2:
            mid_row = src_row + dr // 2
            mid_col = src_col + dc // 2
            mid_piece = self.board[mid_row][mid_col]
            if mid_piece is None:
                return False
            mid_color = self.canvas.itemcget(mid_piece, "fill")
            if piece_color == RED_PIECE and mid_color == BLACK_PIECE:
                return True
            if piece_color == BLACK_PIECE and mid_color == RED_PIECE:
                return True
        return False

    def can_jump(self, row, col):
        directions = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
        for dr, dc in directions:
            new_row = row + dr
            new_col = col + dc
            if 0 <= new_row < ROWS and 0 <= new_col < COLS:
                if self.valid_move(row, col, new_row, new_col):
                    return True
        return False

    def ai_move(self):
        black_pieces = []
        for r in range(ROWS):
            for c in range(COLS):
                piece = self.board[r][c]
                if piece and self.canvas.itemcget(piece, "fill") == BLACK_PIECE:
                    black_pieces.append((r, c))

        # Mandatory jumps: filter only pieces that can jump
        jump_pieces = [p for p in black_pieces if self.can_jump(p[0], p[1])]
        if self.mandatory_jump and jump_pieces:
            black_pieces = jump_pieces

        random.shuffle(black_pieces)

        for r, c in black_pieces:
            # Try jumps first
            for dr, dc in [(-2,-2), (-2,2), (2,-2), (2,2)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < ROWS and 0 <= nc < COLS and self.valid_move(r, c, nr, nc):
                    self.selected_piece = (r, c)
                    self.move_piece(nr, nc)
                    return

            # Try normal moves
            for dr, dc in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < ROWS and 0 <= nc < COLS and self.valid_move(r, c, nr, nc):
                    self.selected_piece = (r, c)
                    self.move_piece(nr, nc)
                    return

        self.turn = 'red'

def rule_menu():
    root = tk.Tk()
    root.title("Checkers Rules")
    root.geometry("400x300")

    mode_var = tk.StringVar(value="AI")
    mandatory_jump_var = tk.BooleanVar(value=True)
    move_after_touch_var = tk.BooleanVar(value=True)

    def start_game():
        root.destroy()
        game_root = tk.Tk()
        Checkers(game_root,
                 mode=mode_var.get(),
                 mandatory_jump=mandatory_jump_var.get(),
                 move_after_touch=move_after_touch_var.get())
        game_root.mainloop()

    tk.Label(root, text="Select Game Mode", font=("Arial", 16)).pack(pady=10)
    tk.Radiobutton(root, text="Play vs AI", variable=mode_var, value="AI").pack()
    tk.Radiobutton(root, text="2 Player", variable=mode_var, value="2P").pack()

    tk.Label(root, text="Rules", font=("Arial", 16)).pack(pady=10)
    tk.Checkbutton(root, text="Mandatory Jumps", variable=mandatory_jump_var).pack()
    tk.Checkbutton(root, text="Move After Touch", variable=move_after_touch_var).pack()

    tk.Button(root, text="Start Game", command=start_game, width=20).pack(pady=20)
    root.mainloop()


if __name__ == "__main__":
    rule_menu()
