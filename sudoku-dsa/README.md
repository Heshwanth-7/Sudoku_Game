<<<<<<< HEAD
# Sudoku (Stack + Linked List)

A full-stack Sudoku game: **Flask REST backend** + **browser frontend** (plain HTML/CSS/JS), plus an optional console version.
The **stack** and **linked list** are implemented from scratch and are used in the real game logic, not just for show.

## Where the data structures are used

| Structure | File | Used for |
|-----------|------|----------|
| `LinkedList` | `sudoku/linked_list.py` | Empty-cell queue for the solver, chronological move log (`history`), hint pool |
| `Stack` (built on `LinkedList`) | `sudoku/stack.py` | Undo stack, redo stack, and the **explicit backtracking stack** of the solver (no recursion) |

Complexity: `push`, `pop`, `peek`, `append`, `prepend`, `pop_front` are all **O(1)**.

## Features

- Puzzle generator (easy / medium / hard) that guarantees a **unique solution**
- Iterative backtracking solver (stack-based), most-constrained-cell-first
- Unlimited **undo / redo**
- Hints, error checking, rule-conflict highlighting, reveal solution
- **Game analysis**: time, moves, mistakes, accuracy, hints, undos, score,
  plus solver statistics of the puzzle (steps, backtracks, max stack depth)
- Unit tests

## Architecture

```
Browser (frontend/)  --fetch JSON-->  Flask API (app.py)  -->  Game engine (sudoku/)
 index.html, style.css, app.js                                  Stack + LinkedList
```

The solution never leaves the server (unless the player gives up), so the game cannot be cheated from dev tools.

### REST API

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/games` `{"difficulty":"easy\|medium\|hard"}` | create a game |
| GET | `/api/games/<id>` | current state |
| POST | `/api/games/<id>/move` `{"row","col","value"}` (0-based, value 0 clears) | place a number |
| POST | `/api/games/<id>/undo` , `/redo` | pop from undo / redo stack |
| POST | `/api/games/<id>/hint` | reveal one correct cell |
| GET | `/api/games/<id>/check` | list wrong cells |
| POST | `/api/games/<id>/solve` | give up, reveal solution |
| GET | `/api/games/<id>/analysis` | player + solver statistics |
| GET | `/api/games/<id>/history` | last 30 actions (linked list) |

## Run

```bash
pip install -r requirements.txt
python app.py                     # open http://127.0.0.1:5000
python main.py hard               # optional console version (no Flask needed)
python -m unittest discover -s tests -t .
```

Games are kept in server memory (last 200), so restarting the server clears them.

### Browser controls
Click a cell, then press `1-9` (or use the number pad). `0` / Backspace clears, arrow keys move,
`Ctrl+Z` / `Ctrl+Y` undo / redo.

## How to play

```
3 4 7        place 7 at row 3, column 4
clear 3 4    empty that cell
undo / redo  move back / forward
hint         reveal one correct cell (-50 score)
check        list wrong cells
analysis     statistics
history 5    last 5 actions
solve        reveal the solution
new hard     start a new game
```

## Project layout

```
sudoku-dsa/
├── app.py                  # backend: Flask REST API
├── frontend/               # index.html, style.css, app.js
├── main.py                 # optional console interface
├── requirements.txt
├── sudoku/
│   ├── linked_list.py      # Node + LinkedList
│   ├── stack.py            # Stack (on top of LinkedList)
│   ├── solver.py           # stack-based backtracking + statistics
│   ├── generator.py        # unique-solution puzzle generator
│   └── game.py             # game state, undo/redo, hints, analysis
└── tests/                  # engine tests + API tests
```

## Upload to GitHub

```bash
cd sudoku-dsa
git init
git add .
git commit -m "Sudoku game using stack and linked list"
git branch -M main
git remote add origin https://github.com/<your-username>/sudoku-dsa.git
git push -u origin main
```
=======
# Sudoku
>>>>>>> 2b534e020c267ae916cef0d00d8bc5dc025981e9
