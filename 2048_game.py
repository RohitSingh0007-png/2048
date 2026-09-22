"""
2048 Game - Simple Python (Tkinter) 

Only basic, beginner-level concepts are used here:
  - Variables, lists (2D list for the board)
  - Functions
  - One simple class to hold the game data
  - if/else, for loops
  - Tkinter basic widgets: Label, Button, Frame, Entry
  - File handling with json (to save/load the leaderboard)
  - Keyboard event binding (bind)

import tkinter as tk
from tkinter import messagebox
import random
import json
import os

# ---------------- Constants ----------------
SIZE = 4
SCORE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scores.json")

# Background color for each tile value
TILE_COLORS = {
    0: "#cdc1b4",
    2: "#eee4da",
    4: "#ede0c8",
    8: "#f2b179",
    16: "#f59563",
    32: "#f67c5f",
    64: "#f65e3b",
    128: "#edcf72",
    256: "#edcc61",
    512: "#edc850",
    1024: "#edc53f",
    2048: "#edc22e",
    4096: "#3c3a32",
}

# Text color for each tile value
TEXT_COLORS = {
    0: "#cdc1b4",
    2: "#776e65",
    4: "#776e65",
}
DEFAULT_TEXT_COLOR = "white"

# Simple color theme for the whole app
BG_COLOR = "#faf6f0"       # page background
PANEL_COLOR = "#ffffff"    # card/box background
BOARD_COLOR = "#bbada0"    # board background (behind the tiles)
BUTTON_COLOR = "#6c5ce7"   # purple buttons
BUTTON_COLOR2 = "#00b894"  # green buttons
TEXT_COLOR = "#2d2b3a"     # normal dark text
MUTED_COLOR = "#7a7690"    # grey/secondary text
FONT_NAME = "Helvetica"


def make_button(parent, text, bg_color, command, font_size=12, padx=20, pady=10):
    """A clickable colored button.

    Note: on macOS, tkinter's normal Button widget ignores the bg color
    you give it (it always shows the native grey Mac button), which made
    the white text invisible. A Label reacting to a mouse click behaves
    the same as a button but its colors always show correctly on every
    operating system, so we use that instead.
    """
    btn = tk.Label(parent, text=text, bg=bg_color, fg="white",
                   font=(FONT_NAME, font_size, "bold"),
                   padx=padx, pady=pady, cursor="hand2")
    btn.bind("<Button-1>", lambda event: command())
    return btn


# ---------------- Game Logic ----------------
class Game2048:
    """Stores the board and score, and has functions to move/merge tiles."""

    def __init__(self):
        self.reset()

    def reset(self):
        # Create a 4x4 board filled with zeros (0 = empty cell)
        self.board = []
        for i in range(SIZE):
            row = [0, 0, 0, 0]
            self.board.append(row)

        self.score = 0
        self.game_over = False
        self.won = False

        self.spawn_tile()
        self.spawn_tile()

    def spawn_tile(self):
        """Put a new 2 or 4 in a random empty cell."""
        empty_cells = []
        for r in range(SIZE):
            for c in range(SIZE):
                if self.board[r][c] == 0:
                    empty_cells.append((r, c))

        if len(empty_cells) == 0:
            return

        r, c = random.choice(empty_cells)
        chance = random.random()  # a random number between 0 and 1
        if chance < 0.1:
            self.board[r][c] = 4
        else:
            self.board[r][c] = 2

    def compress(self, row):
        """Push all non-zero numbers to the left, fill rest with 0."""
        new_row = []
        for value in row:
            if value != 0:
                new_row.append(value)
        while len(new_row) < SIZE:
            new_row.append(0)
        return new_row

    def merge(self, row):
        """Combine two equal neighbouring tiles into one, left to right."""
        for i in range(SIZE - 1):
            if row[i] != 0 and row[i] == row[i + 1]:
                row[i] = row[i] * 2
                self.score = self.score + row[i]
                if row[i] == 2048:
                    self.won = True
                row[i + 1] = 0
        return row

    def move_row_left(self, row):
        row = self.compress(row)
        row = self.merge(row)
        row = self.compress(row)
        return row

    def reverse_row(self, row):
        return row[::-1]

    def transpose(self):
        """Swap rows and columns (used for Up and Down moves)."""
        new_board = []
        for c in range(SIZE):
            new_row = []
            for r in range(SIZE):
                new_row.append(self.board[r][c])
            new_board.append(new_row)
        self.board = new_board

    def move(self, direction):
        """direction is 'Left', 'Right', 'Up' or 'Down'."""
        old_board = []
        for row in self.board:
            old_board.append(row[:])  # copy each row

        if direction == "Left":
            for i in range(SIZE):
                self.board[i] = self.move_row_left(self.board[i])

        elif direction == "Right":
            for i in range(SIZE):
                reversed_row = self.reverse_row(self.board[i])
                moved_row = self.move_row_left(reversed_row)
                self.board[i] = self.reverse_row(moved_row)

        elif direction == "Up":
            self.transpose()
            for i in range(SIZE):
                self.board[i] = self.move_row_left(self.board[i])
            self.transpose()

        elif direction == "Down":
            self.transpose()
            for i in range(SIZE):
                reversed_row = self.reverse_row(self.board[i])
                moved_row = self.move_row_left(reversed_row)
                self.board[i] = self.reverse_row(moved_row)
            self.transpose()

        moved = (self.board != old_board)

        if moved:
            self.spawn_tile()
            if not self.can_move():
                self.game_over = True

        return moved

    def can_move(self):
        """Return True if an empty cell exists OR two equal neighbours exist."""
        for r in range(SIZE):
            for c in range(SIZE):
                if self.board[r][c] == 0:
                    return True
                if c + 1 < SIZE and self.board[r][c] == self.board[r][c + 1]:
                    return True
                if r + 1 < SIZE and self.board[r][c] == self.board[r + 1][c]:
                    return True
        return False


# ---------------- Leaderboard functions (JSON file) ----------------
def load_scores():
    if not os.path.exists(SCORE_FILE):
        return []
    try:
        with open(SCORE_FILE, "r") as f:
            data = json.load(f)
        data.sort(key=lambda x: x["score"], reverse=True)
        return data
    except Exception:
        return []


def save_score(name, score):
    scores = load_scores()
    scores.append({"name": name, "score": score})
    scores.sort(key=lambda x: x["score"], reverse=True)
    top3 = scores[:3]
    with open(SCORE_FILE, "w") as f:
        json.dump(top3, f, indent=2)
    return top3


# ---------------- GUI ----------------
class App(tk.Tk):
    """Main window. Switches between 4 pages using simple Frames."""

    def __init__(self):
        super().__init__()
        self.title("2048")
        self.geometry("420x620")
        self.resizable(False, False)
        self.configure(bg=BG_COLOR)

        self.game = Game2048()
        self.player_name = "Player"

        # Create all 4 pages and stack them on top of each other
        self.welcome_frame = WelcomeFrame(self, self)
        self.name_frame = NameFrame(self, self)
        self.instructions_frame = InstructionsFrame(self, self)
        self.game_frame = GameFrame(self, self)

        for frame in (self.welcome_frame, self.name_frame,
                      self.instructions_frame, self.game_frame):
            frame.place(x=0, y=0, relwidth=1, relheight=1)

        self.show_frame(self.welcome_frame)

        self.bind("<Key>", self.on_key_press)

    def show_frame(self, frame):
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show()

    def on_key_press(self, event):
        if not self.game_frame.winfo_ismapped():
            return  # only respond to keys while the game page is visible

        key = event.keysym
        if key in ("Left", "a", "A"):
            self.game_frame.handle_move("Left")
        elif key in ("Right", "d", "D"):
            self.game_frame.handle_move("Right")
        elif key in ("Up", "w", "W"):
            self.game_frame.handle_move("Up")
        elif key in ("Down", "s", "S"):
            self.game_frame.handle_move("Down")


class WelcomeFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG_COLOR)

        tk.Label(self, text="2048", font=(FONT_NAME, 40, "bold"),
                 fg=BUTTON_COLOR, bg=BG_COLOR).pack(pady=(150, 10))

        tk.Label(self, text="Welcome! The classic tile-merging game.",
                 font=(FONT_NAME, 12), fg=MUTED_COLOR, bg=BG_COLOR).pack(pady=(0, 30))

        make_button(self, "Click to Start", BUTTON_COLOR,
                    lambda: app.show_frame(app.name_frame), font_size=13).pack()


class NameFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG_COLOR)
        self.app = app

        tk.Label(self, text="2048", font=(FONT_NAME, 28, "bold"),
                 fg=BUTTON_COLOR, bg=BG_COLOR).pack(pady=(30, 15))

        tk.Label(self, text="Top 3 Scores", font=(FONT_NAME, 14, "bold"),
                 fg=TEXT_COLOR, bg=BG_COLOR).pack(pady=(10, 5))

        self.leaderboard_frame = tk.Frame(self, bg=PANEL_COLOR)
        self.leaderboard_frame.pack(padx=40, pady=5, fill="x")

        tk.Label(self, text="Enter your name:", font=(FONT_NAME, 12),
                 fg=MUTED_COLOR, bg=BG_COLOR).pack(pady=(30, 5))

        self.name_entry = tk.Entry(self, font=(FONT_NAME, 13), justify="center")
        self.name_entry.pack(pady=5, ipady=5, padx=40, fill="x")

        make_button(self, "Start Game", BUTTON_COLOR,
                    self.start_game, font_size=13).pack(pady=25)

    def on_show(self):
        self.render_leaderboard()

    def render_leaderboard(self):
        # Remove old labels before drawing new ones
        for widget in self.leaderboard_frame.winfo_children():
            widget.destroy()

        scores = load_scores()
        if len(scores) == 0:
            tk.Label(self.leaderboard_frame, text="No scores yet!",
                     fg=MUTED_COLOR, bg=PANEL_COLOR).pack(pady=10)
            return

        rank = 1
        for entry in scores:
            row = tk.Frame(self.leaderboard_frame, bg=PANEL_COLOR)
            row.pack(fill="x", padx=10, pady=3)
            tk.Label(row, text=f"{rank}. {entry['name']}", fg=TEXT_COLOR,
                     bg=PANEL_COLOR, font=(FONT_NAME, 11, "bold")).pack(side="left")
            tk.Label(row, text=str(entry['score']), fg=BUTTON_COLOR,
                     bg=PANEL_COLOR, font=(FONT_NAME, 11, "bold")).pack(side="right")
            rank = rank + 1

    def start_game(self):
        name = self.name_entry.get().strip()
        if name == "":
            name = "Player"
        self.app.player_name = name
        self.app.game.reset()
        self.app.show_frame(self.app.instructions_frame)


INSTRUCTIONS_TEXT = (
    "1. The game starts with two tiles (2 or 4).\n\n"
    "2. Use Arrow Keys or W/A/S/D to move all tiles.\n\n"
    "3. When two tiles with the same number touch, they merge into one.\n\n"
    "4. The goal is to create the 2048 tile.\n\n"
    "5. The game ends when there are no empty spaces and no valid moves."
)


class InstructionsFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG_COLOR)

        tk.Label(self, text="How to Play", font=(FONT_NAME, 20, "bold"),
                 fg=BUTTON_COLOR, bg=BG_COLOR).pack(pady=(60, 20))

        tk.Label(self, text=INSTRUCTIONS_TEXT, font=(FONT_NAME, 11),
                 fg=TEXT_COLOR, bg=BG_COLOR, justify="left",
                 wraplength=340).pack(padx=30)

        make_button(self, "Let's Play!", BUTTON_COLOR2,
                    lambda: app.show_frame(app.game_frame), font_size=13).pack(pady=30)


class GameFrame(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg=BG_COLOR)
        self.app = app
        self.best_score = 0

        # ---- Header: title + score boxes ----
        header = tk.Frame(self, bg=BG_COLOR)
        header.pack(fill="x", padx=15, pady=15)

        tk.Label(header, text="2048", font=(FONT_NAME, 26, "bold"),
                 fg=BUTTON_COLOR, bg=BG_COLOR).pack(side="left")

        score_box = tk.Frame(header, bg=PANEL_COLOR)
        score_box.pack(side="right", padx=5)
        tk.Label(score_box, text="SCORE", font=(FONT_NAME, 9, "bold"),
                 fg=MUTED_COLOR, bg=PANEL_COLOR).pack(padx=15, pady=(5, 0))
        self.score_label = tk.Label(score_box, text="0", font=(FONT_NAME, 16, "bold"),
                                     fg=TEXT_COLOR, bg=PANEL_COLOR)
        self.score_label.pack(padx=15, pady=(0, 5))

        best_box = tk.Frame(header, bg=PANEL_COLOR)
        best_box.pack(side="right", padx=5)
        tk.Label(best_box, text="BEST", font=(FONT_NAME, 9, "bold"),
                 fg=MUTED_COLOR, bg=PANEL_COLOR).pack(padx=15, pady=(5, 0))
        self.best_label = tk.Label(best_box, text="0", font=(FONT_NAME, 16, "bold"),
                                    fg=TEXT_COLOR, bg=PANEL_COLOR)
        self.best_label.pack(padx=15, pady=(0, 5))

        # ---- Control buttons ----
        controls = tk.Frame(self, bg=BG_COLOR)
        controls.pack(fill="x", padx=15)
        make_button(controls, "New Game", BUTTON_COLOR, self.new_game,
                    font_size=11, padx=15, pady=6).pack(side="left")
        make_button(controls, "How to Play", BUTTON_COLOR2, self.show_instructions,
                    font_size=11, padx=15, pady=6).pack(side="right")

        # ---- The board: a simple grid of Label widgets ----
        board_frame = tk.Frame(self, bg=BOARD_COLOR)
        board_frame.pack(padx=15, pady=15)

        self.cells = []  # 2D list of Label widgets, one per board cell
        for r in range(SIZE):
            row_cells = []
            for c in range(SIZE):
                cell = tk.Label(board_frame, text="", width=4, height=2,
                                 font=(FONT_NAME, 20, "bold"), bg=TILE_COLORS[0])
                cell.grid(row=r, column=c, padx=6, pady=6)
                row_cells.append(cell)
            self.cells.append(row_cells)

    def on_show(self):
        self.best_score = 0
        self.render_board()

    def new_game(self):
        self.app.game.reset()
        self.render_board()

    def handle_move(self, direction):
        game = self.app.game
        if game.game_over:
            return

        moved = game.move(direction)
        if moved:
            self.render_board()
            if game.won:
                self.end_game(True)
            elif game.game_over:
                self.end_game(False)

    def render_board(self):
        """Update every Label's text and color to match the board."""
        game = self.app.game
        for r in range(SIZE):
            for c in range(SIZE):
                value = game.board[r][c]
                cell = self.cells[r][c]
                if value == 0:
                    cell.config(text="", bg=TILE_COLORS[0])
                else:
                    bg_color = TILE_COLORS.get(value, "#3c3a32")
                    fg_color = TEXT_COLORS.get(value, DEFAULT_TEXT_COLOR)
                    cell.config(text=str(value), bg=bg_color, fg=fg_color)

        self.score_label.config(text=str(game.score))
        if game.score > self.best_score:
            self.best_score = game.score
        self.best_label.config(text=str(self.best_score))

    def show_instructions(self):
        messagebox.showinfo("How to Play", INSTRUCTIONS_TEXT)

    def end_game(self, won):
        game = self.app.game
        scores = save_score(self.app.player_name, game.score)

        if won:
            title = "You Win!"
        else:
            title = "Game Over!"

        board_text = ""
        rank = 1
        for entry in scores:
            board_text = board_text + f"{rank}. {entry['name']} - {entry['score']}\n"
            rank = rank + 1

        message = f"{title}\nYour score: {game.score}\n\nTop 3 Scores:\n{board_text}\nPlay again?"
        play_again = messagebox.askyesno(title, message)

        if play_again:
            self.app.show_frame(self.app.name_frame)
        else:
            self.app.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
