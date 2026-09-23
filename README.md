![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-blue.svg)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![Status](https://img.shields.io/badge/status-complete-brightgreen.svg)

# 2048 — Python Edition

**A classic 2048 tile-merging puzzle game, built entirely in Python with a Tkinter GUI.**

2048 is a single-player puzzle game where tiles of matching numbers are merged by sliding them across a 4×4 board, with the goal of creating a tile worth 2048. This implementation is written end-to-end in Python — no HTML, CSS, or JavaScript — using Tkinter for the interface, a plain 2D list for the game state, and a local JSON file as a lightweight leaderboard store. It was built as a Python PBL (Project-Based Learning) project to demonstrate core Python concepts (data structures, functions, OOP, file handling, and event-driven GUI programming) in one complete, playable application.

---

## Table of Contents

- [How It Works](#how-it-works)
- [Demo](#demo)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Project Status](#project-status)
- [Scope & Limitations](#scope--limitations)
- [Future Work](#future-work)
- [Team](#team)
- [References](#references)
- [License](#license)

---

## How It Works

The project is split into two independent parts:

1. A **`Game2048`** class that owns all game state and rules — the board (a 4×4 list of lists), the score, and the move/merge logic. It has no knowledge of Tkinter at all.
2. A set of **Tkinter `Frame`** screens (Welcome → Name entry → Instructions → Game) that only handle what the player sees and does, and call into `Game2048` for every game decision.

A move happens in three steps per row: **compress** (slide non-zero tiles together), **merge** (combine equal neighbouring tiles once), then **compress** again. Right, Up, and Down moves reuse this same left-move logic — Right by reversing each row before and after, Up/Down by transposing the board (swapping rows and columns) before and after. After every valid move, a new tile spawns randomly (90% chance of a `2`, 10% chance of a `4`), and the game ends the moment no empty cell and no matching neighbours remain.

See [`2048_game.py`](2048_game.py) — the whole project is intentionally kept in a single, readable file.

## Demo

The game opens full-screen: a Welcome screen, then a name-entry screen showing the live Top-3 leaderboard, then a short instructions screen, then the game itself. Score and Best Score update live in the header as tiles merge, and on game over the final score is saved automatically and the updated leaderboard is shown.

## Architecture

```
        App (tk.Tk window, full screen)
                    │
    ┌───────────────┼────────────────┬─────────────┐
    ▼               ▼                ▼              ▼
WelcomeFrame    NameFrame     InstructionsFrame   GameFrame
                    │                                 │
                    ▼                                 ▼
            scores.json (leaderboard)         Game2048 (board, score,
            read/written via json module        move/merge/spawn logic)
```

All four screens are stacked in the same window and switched with `tkraise()` — no new windows are opened. `GameFrame` is the only screen that talks to `Game2048`; `Game2048` never touches Tkinter.

## Tech Stack

| Technology | Role |
|---|---|
| Python 3.10+ | Core language — logic and GUI, entirely |
| Tkinter | Standard-library GUI toolkit — windows, frames, labels, buttons |
| `json` | Saving/loading the local leaderboard file |
| `random` | Random tile spawning (2 vs 4) and empty-cell selection |
| `os` | Locating the leaderboard file next to the script |

No third-party packages and nothing to `pip install` — a fresh Python 3 install is enough.

## Getting Started

**Prerequisites:**
- Python 3.10+ (Tkinter ships with the standard Python installer on Windows/macOS; on Linux it may need `sudo apt install python3-tk`)

**Setup:**
```bash
git clone https://github.com/RohitSingh0007/2048-python-game.git
cd 2048-python-game
python3 2048_game.py
```
The game window opens automatically, sized to the full screen.

## Project Status

Currently **complete** for its intended scope as a PBL submission.

- [x] Core game logic (board, moves, merging, spawning, win/loss detection)
- [x] Multi-screen Tkinter GUI (Welcome, Name entry, Instructions, Game)
- [x] Score and Best Score tracking
- [x] Persistent Top-3 leaderboard (`scores.json`)
- [x] Full keyboard controls (Arrow keys + WASD)
- [x] Cross-platform button rendering fix (macOS Tkinter styling issue)
- [x] Full-screen, centered layout
- [ ] Sound effects
- [ ] Undo move
- [ ] Configurable board size

## Scope & Limitations

- **Single-player, local only.** No networked multiplayer or online leaderboard — the leaderboard is a local `scores.json` file next to the script.
- **Fixed 4×4 board.** The board size is a constant (`SIZE = 4`) rather than user-configurable, though the logic itself would work unchanged at other sizes.
- **No animations.** Tile movement is instant, by design — this keeps every part of the code explainable with only beginner/intermediate Python and Tkinter concepts.
- **Desktop only.** Tkinter produces a native desktop window; there is no mobile or web version.

## Future Work

- Add optional sound effects for merges and game over
- Add an "Undo" button that restores the previous board state
- Make board size configurable (e.g. 5×5, 6×6) from the Welcome screen
- Add a light "how you're doing vs. your best" progress indicator

## Team

| Name | Role |
|---|---|
| Rohit Singh | Team Lead |
| Pranjal Rawat | Member |


## References

- [Python `tkinter` documentation](https://docs.python.org/3/library/tkinter.html)
- [Python `json` documentation](https://docs.python.org/3/library/json.html)

## License

- This project is licensed under the MIT License.
