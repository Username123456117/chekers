import tkinter as tk

# Constants
ROWS, COLS = 8, 8
SQUARE_SIZE = 60

# Colors
LIGHT_SQUARE = "#EEEED2"
DARK_SQUARE = "#769656"
RED_PIECE = "#FF0000"
BLACK_PIECE = "#000000"

class Checkers:
    def __init__(self, root):
        self.root = root
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

        if self.selected_piece:
            self.move_piece(row, col)
        elif piece:
            piece_color = self.canvas.itemcget(piece, "fill")
            if (self.turn == 'red' and piece_color == RED_PIECE) or \
               (self.turn == 'black' and piece_color == BLACK_PIECE):
                self.selected_piece = (row, col)

    def move_piece(self, row, col):
        src_row, src_col = self.selected_piece
        piece = self.board[src_row][src_col]

        if self.valid_move(src_row, src_col, row, col):
            self.canvas.move(piece, (col - src_col)*SQUARE_SIZE, (row - src_row)*SQUARE_SIZE)
            self.board[row][col] = piece
            self.board[src_row][src_col] = None
            self.turn = 'black' if self.turn == 'red' else 'red'

        self.selected_piece = None

    def valid_move(self, src_row, src_col, dest_row, dest_col):
        # Only basic moves: diagonal by 1, no jumps yet
        if self.board[dest_row][dest_col] is not None:
            return False
        dr = dest_row - src_row
        dc = abs(dest_col - src_col)
        piece_color = self.canvas.itemcget(self.board[src_row][src_col], "fill")
        if dc == 1:
            if piece_color == RED_PIECE and dr == -1:
                return True
            if piece_color == BLACK_PIECE and dr == 1:
                return True
        return False

if __name__ == "__main__":
    root = tk.Tk()
    game = Checkers(root)
    root.mainloop()
