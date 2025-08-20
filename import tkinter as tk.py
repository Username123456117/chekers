import tkinter as tk
from tkinter import ttk, colorchooser
import random
import copy

# Constants
DEFAULT_ROWS, DEFAULT_COLS = 8, 8
DEFAULT_PIECES = 12
SQUARE_SIZE = 60

class CheckersGame:
    def __init__(self, master):
        self.master = master
        master.title("Checkers Full Game")

        # Game variables
        self.rows = DEFAULT_ROWS
        self.cols = DEFAULT_COLS
        self.pieces_per_player = DEFAULT_PIECES
        self.turn = 'red'
        self.mode = "AI"
        self.difficulty = "Easy"
        self.mandatory_jump = True
        self.move_after_touch = True

        # Colors
        self.light_square = "#EEEED2"
        self.dark_square = "#769656"
        self.red_piece_color = "#FF0000"
        self.black_piece_color = "#000000"
        self.king_outline = "#FFD700"

        # Piece counts
        self.red_count = tk.IntVar(value=self.pieces_per_player)
        self.black_count = tk.IntVar(value=self.pieces_per_player)

        # Undo history
        self.history = []

        # Notebook Tabs
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(fill='both', expand=True)

        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="Settings")
        self.create_settings_tab()

        self.game_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.game_tab, text="Game")

        self.top_frame = tk.Frame(self.game_tab)
        self.top_frame.pack()
        self.red_label = tk.Label(self.top_frame, text=f"Red Pieces: {self.red_count.get()}", font=("Arial", 14))
        self.red_label.pack(side="left", padx=10)
        self.black_label = tk.Label(self.top_frame, text=f"Black Pieces: {self.black_count.get()}", font=("Arial", 14))
        self.black_label.pack(side="right", padx=10)

        self.canvas = tk.Canvas(self.game_tab, width=self.cols*SQUARE_SIZE, height=self.rows*SQUARE_SIZE)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.click)

        self.undo_btn = tk.Button(self.game_tab, text="Undo", command=self.undo)
        self.undo_btn.pack(pady=5)

        # Initialize game state
        self.selected_piece = None
        self.board = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.piece_info = {}
        self.draw_board()
        self.place_pieces()

    # ------------------ Settings Tab ------------------
    def create_settings_tab(self):
        frame = self.settings_tab

        tk.Label(frame, text="Board Size").pack(pady=5)
        self.board_size_var = tk.IntVar(value=self.rows)
        tk.Scale(frame, from_=6, to=12, orient=tk.HORIZONTAL, variable=self.board_size_var).pack()

        tk.Label(frame, text="Pieces per Player").pack(pady=5)
        self.pieces_var = tk.IntVar(value=self.pieces_per_player)
        tk.Scale(frame, from_=4, to=20, orient=tk.HORIZONTAL, variable=self.pieces_var).pack()

        tk.Label(frame, text="Players").pack(pady=5)
        self.mode_var = tk.StringVar(value="AI")
        tk.Radiobutton(frame, text="Play vs AI", variable=self.mode_var, value="AI").pack()
        tk.Radiobutton(frame, text="2 Players", variable=self.mode_var, value="2P").pack()

        tk.Label(frame, text="AI Difficulty").pack(pady=5)
        self.difficulty_var = tk.StringVar(value="Easy")
        for level in ["Easy","Medium","Adaptive","Hard","Impossible"]:
            tk.Radiobutton(frame, text=level, variable=self.difficulty_var, value=level).pack()

        tk.Label(frame, text="Rules").pack(pady=5)
        self.mandatory_jump_var = tk.BooleanVar(value=True)
        self.move_after_touch_var = tk.BooleanVar(value=True)
        tk.Checkbutton(frame, text="Mandatory Jumps", variable=self.mandatory_jump_var).pack()
        tk.Checkbutton(frame, text="Move After Touch", variable=self.move_after_touch_var).pack()

        tk.Label(frame, text="Board Colors").pack(pady=5)
        tk.Button(frame, text="Light Squares", command=lambda: self.choose_color('light')).pack()
        tk.Button(frame, text="Dark Squares", command=lambda: self.choose_color('dark')).pack()
        tk.Button(frame, text="Red Pieces", command=lambda: self.choose_color('red')).pack()
        tk.Button(frame, text="Black Pieces", command=lambda: self.choose_color('black')).pack()

        # Manual piece counts
        tk.Label(frame, text="Manual Piece Count Adjustments").pack(pady=5)
        tk.Label(frame, text="Red Pieces").pack()
        self.red_count_var = tk.IntVar(value=self.pieces_per_player)
        tk.Spinbox(frame, from_=0, to=99, textvariable=self.red_count_var).pack()
        tk.Label(frame, text="Black Pieces").pack()
        self.black_count_var = tk.IntVar(value=self.pieces_per_player)
        tk.Spinbox(frame, from_=0, to=99, textvariable=self.black_count_var).pack()

        tk.Button(frame, text="Apply & Start Game", command=self.apply_settings).pack(pady=10)

    def choose_color(self, target):
        color_code = colorchooser.askcolor(title=f"Choose {target} color")[1]
        if color_code:
            if target=='light':
                self.light_square = color_code
            elif target=='dark':
                self.dark_square = color_code
            elif target=='red':
                self.red_piece_color = color_code
            elif target=='black':
                self.black_piece_color = color_code
            self.draw_board()
            self.place_pieces()

    def apply_settings(self):
        self.rows = self.board_size_var.get()
        self.cols = self.board_size_var.get()
        self.pieces_per_player = self.pieces_var.get()
        self.mode = self.mode_var.get()
        self.difficulty = self.difficulty_var.get()
        self.mandatory_jump = self.mandatory_jump_var.get()
        self.move_after_touch = self.move_after_touch_var.get()
        self.turn = 'red'
        self.selected_piece = None
        self.history = []

        # Piece counts
        self.red_count.set(self.red_count_var.get())
        self.black_count.set(self.black_count_var.get())

        self.board = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.piece_info = {}
        self.canvas.config(width=self.cols*SQUARE_SIZE, height=self.rows*SQUARE_SIZE)
        self.draw_board()
        self.place_pieces()
        self.update_counters()

        # Switch to Game tab
        self.notebook.select(self.game_tab)

    # ------------------ Board & Pieces ------------------
    def draw_board(self):
        self.canvas.delete("all")
        for r in range(self.rows):
            for c in range(self.cols):
                color = self.light_square if (r+c)%2==0 else self.dark_square
                self.canvas.create_rectangle(c*SQUARE_SIZE,r*SQUARE_SIZE,(c+1)*SQUARE_SIZE,(r+1)*SQUARE_SIZE,fill=color)

    def place_pieces(self):
        self.piece_info.clear()
        rows_needed = (self.pieces_per_player + (self.cols//2 -1)) // (self.cols//2)
        count = 0
        # Top rows black
        for r in range(rows_needed):
            for c in range(self.cols):
                if (r+c)%2 !=0 and count<self.pieces_per_player:
                    self.create_piece(r,c,self.black_piece_color)
                    count+=1
        count=0
        # Bottom rows red
        for r in range(self.rows-rows_needed,self.rows):
            for c in range(self.cols):
                if (r+c)%2 !=0 and count<self.pieces_per_player:
                    self.create_piece(r,c,self.red_piece_color)
                    count+=1

    def create_piece(self,row,col,color):
        x1 = col*SQUARE_SIZE+10
        y1 = row*SQUARE_SIZE+10
        x2 = x1+SQUARE_SIZE-20
        y2 = y1+SQUARE_SIZE-20
        piece = self.canvas.create_oval(x1,y1,x2,y2,fill=color,width=2)
        self.board[row][col]=piece
        self.piece_info[piece] = {"color":color,"king":False}

    # ------------------ Click & Move ------------------
    def click(self,event):
        col = event.x // SQUARE_SIZE
        row = event.y // SQUARE_SIZE
        if row>=self.rows or col>=self.cols:
            return
        piece = self.board[row][col]

        # Determine mandatory jumps
        jump_pieces=[]
        if self.mandatory_jump:
            for r in range(self.rows):
                for c in range(self.cols):
                    p = self.board[r][c]
                    if p and self.piece_info[p]["color"]==(self.red_piece_color if self.turn=="red" else self.black_piece_color):
                        if self.can_jump(r,c):
                            jump_pieces.append((r,c))

        if piece:
            info = self.piece_info[piece]
            if info["color"]==(self.red_piece_color if self.turn=="red" else self.black_piece_color):
                if self.mandatory_jump and jump_pieces and (row,col) not in jump_pieces:
                    return
                if self.move_after_touch:
                    if self.selected_piece==(row,col):
                        self.selected_piece=None
                    elif self.selected_piece is None:
                        self.selected_piece=(row,col)
                else:
                    self.selected_piece=(row,col)
        elif self.selected_piece:
            self.save_history()
            self.move_piece(row,col)

    def move_piece(self,row,col):
        src_row,src_col = self.selected_piece
        piece = self.board[src_row][src_col]
        info = self.piece_info[piece]

        if self.valid_move(src_row,src_col,row,col):
            dr=row-src_row
            dc=col-src_col
            if abs(dr)==2 and abs(dc)==2:
                mid_r,mid_c = (src_row+row)//2,(src_col+col)//2
                captured=self.board[mid_r][mid_c]
                if captured:
                    self.canvas.delete(captured)
                    self.board[mid_r][mid_c]=None
                    del self.piece_info[captured]
                    if info["color"]==self.red_piece_color:
                        self.black_count.set(self.black_count.get()-1)
                    else:
                        self.red_count.set(self.red_count.get()-1)
                    self.update_counters()

            self.canvas.move(piece,dc*SQUARE_SIZE,dr*SQUARE_SIZE)
            self.board[row][col]=piece
            self.board[src_row][src_col]=None

            # Promote to king
            if info["color"]==self.red_piece_color and row==0:
                info["king"]=True
                self.canvas.itemconfig(piece,outline=self.king_outline,width=3)
            elif info["color"]==self.black_piece_color and row==self.rows-1:
                info["king"]=True
                self.canvas.itemconfig(piece,outline=self.king_outline,width=3)

            # Chain jumps
            if abs(dr)==2 and self.can_jump(row,col):
                self.selected_piece=(row,col)
            else:
                self.selected_piece=None
                self.turn='black' if self.turn=='red' else 'red'
                self.check_endgame()
                if self.mode=="AI" and self.turn=='black':
                    self.master.after(300,self.ai_move)
            return True
        return False

    # ------------------ Move Validation ------------------
    def valid_move(self,src_row,src_col,dest_row,dest_col):
        if self.board[dest_row][dest_col] is not None:
            return False
        dr=dest_row-src_row
        dc=dest_col-src_col
        piece=self.board[src_row][src_col]
        info=self.piece_info[piece]
        color = info["color"]
        king = info["king"]

        # Normal move
        if abs(dr)==1 and abs(dc)==1:
            if king:
                return True
            if color==self.red_piece_color and dr==-1:
                return True
            if color==self.black_piece_color and dr==1:
                return True
            return False

        # Jump move
        if abs(dr)==2 and abs(dc)==2:
            mid_r,mid_c=(src_row+dest_row)//2,(src_col+dest_col)//2
            mid_piece=self.board[mid_r][mid_c]
            if mid_piece is None:
                return False
            mid_color=self.piece_info[mid_piece]["color"]
            if king:
                if (color==self.red_piece_color and mid_color==self.black_piece_color) or \
                   (color==self.black_piece_color and mid_color==self.red_piece_color):
                    return True
            else:
                if color==self.red_piece_color and dr==-2 and mid_color==self.black_piece_color:
                    return True
                if color==self.black_piece_color and dr==2 and mid_color==self.red_piece_color:
                    return True
        return False

    def can_jump(self,row,col):
        piece=self.board[row][col]
        if not piece: return False
        directions=[(-2,-2),(-2,2),(2,-2),(2,2)]
        for dr,dc in directions:
            nr,nc=row+dr,col+dc
            if 0<=nr<self.rows and 0<=nc<self.cols:
                if self.valid_move(row,col,nr,nc):
                    return True
        return False

    # ------------------ Undo ------------------
    def save_history(self):
        state = {
            "board": copy.deepcopy(self.board),
            "piece_info": copy.deepcopy(self.piece_info),
            "turn": self.turn,
            "red_count": self.red_count.get(),
            "black_count": self.black_count.get()
        }
        self.history.append(state)

    def undo(self):
        if self.history:
            state = self.history.pop()
            self.board=state["board"]
            self.piece_info=state["piece_info"]
            self.turn=state["turn"]
            self.red_count.set(state["red_count"])
            self.black_count.set(state["black_count"])
            self.update_counters()
            self.draw_board()
            for r in range(self.rows):
                for c in range(self.cols):
                    piece = self.board[r][c]
                    if piece:
                        color=self.piece_info[piece]["color"]
                        self.create_piece(r,c,color)

    # ------------------ AI ------------------
    def ai_move(self):
        black_pieces=[(r,c) for r in range(self.rows) for c in range(self.cols) if self.board[r][c] and self.piece_info[self.board[r][c]]["color"]==self.black_piece_color]
        random.shuffle(black_pieces)
        for r,c in black_pieces:
            piece=self.board[r][c]
            king=self.piece_info[piece]["king"]
            for dr,dc in [(-2,-2),(-2,2),(2,-2),(2,2),(-1,-1),(-1,1),(1,-1),(1,1)]:
                if not king and dr<0: continue
                nr,nc=r+dr,c+dc
                if 0<=nr<self.rows and 0<=nc<self.cols and self.valid_move(r,c,nr,nc):
                    self.selected_piece=(r,c)
                    self.move_piece(nr,nc)
                    return

    # ------------------ Counter Update ------------------
    def update_counters(self):
        self.red_label.config(text=f"Red Pieces: {self.red_count.get()}")
        self.black_label.config(text=f"Black Pieces: {self.black_count.get()}")

    # ------------------ End Screen ------------------
    def check_endgame(self):
        if self.red_count.get() <= 0:
            self.show_end_screen(winner="Black")
        elif self.black_count.get() <= 0:
            self.show_end_screen(winner="Red")

    def show_end_screen(self, winner):
        self.canvas.unbind("<Button-1>")
        self.overlay = tk.Frame(self.game_tab, bg="black", width=self.cols*SQUARE_SIZE,
                                height=self.rows*SQUARE_SIZE)
        self.overlay.place(x=0, y=40)
        msg = tk.Label(self.overlay, text=f"{winner} Wins!", font=("Arial", 24), fg="white", bg="black")
        msg.pack(pady=50)
        restart_btn = tk.Button(self.overlay, text="Restart Game", command=self.restart_game)
        restart_btn.pack(pady=10)
        settings_btn = tk.Button(self.overlay, text="Settings", command=self.back_to_settings)
        settings_btn.pack(pady=10)

    def restart_game(self):
        self.overlay.destroy()
        self.apply_settings()
        self.canvas.bind("<Button-1>", self.click)

    def back_to_settings(self):
        self.overlay.destroy()
        self.notebook.select(self.settings_tab)
        self.canvas.bind("<Button-1>", self.click)

# ------------------ Main ------------------
if __name__=="__main__":
    root=tk.Tk()
    game=CheckersGame(root)
    root.mainloop()
