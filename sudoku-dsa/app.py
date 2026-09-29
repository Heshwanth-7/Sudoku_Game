"""Backend: Flask REST API + static frontend.

Every game lives in memory and is driven by sudoku.game.Game, which uses our
own Stack (undo/redo) and LinkedList (history).  Run:  python app.py
"""

import os
import threading
import uuid

from flask import Flask, jsonify, request, send_from_directory

from sudoku.game import Game
from sudoku.generator import CLUES

FRONTEND = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
app = Flask(__name__, static_folder=FRONTEND, static_url_path="")

GAMES = {}            # game_id -> Game
LOCK = threading.Lock()
MAX_GAMES = 200


def state(game):
    """JSON-safe snapshot. The solution is never sent unless the player gave up."""
    return {
        "difficulty": game.difficulty,
        "puzzle": game.puzzle,
        "board": game.board,
        "conflicts": [[r, c] for r in range(9) for c in range(9) if game.has_conflict(r, c)],
        "solved": game.is_solved(),
        "revealed": game.revealed,
        "moves": game.moves,
        "mistakes": game.mistakes,
        "hints": game.hints,
        "undos": game.undos,
        "can_undo": not game.undo_stack.is_empty(),
        "can_redo": not game.redo_stack.is_empty(),
        "elapsed": round(game.elapsed(), 1),
    }


def find(gid):
    game = GAMES.get(gid)
    if game is None:
        raise KeyError("game not found")
    return game


@app.errorhandler(KeyError)
def not_found(e):
    return jsonify(error=str(e.args[0])), 404


@app.errorhandler(ValueError)
def bad_request(e):
    return jsonify(error=str(e)), 400


@app.get("/")
def index():
    return send_from_directory(FRONTEND, "index.html")


@app.post("/api/games")
def new_game():
    level = (request.get_json(silent=True) or {}).get("difficulty", "medium")
    if level not in CLUES:
        raise ValueError(f"difficulty must be one of {list(CLUES)}")
    game = Game(level)                          # generated outside the lock
    gid = uuid.uuid4().hex[:12]
    with LOCK:
        GAMES[gid] = game
        while len(GAMES) > MAX_GAMES:           # drop the oldest games
            GAMES.pop(next(iter(GAMES)))
    return jsonify(id=gid, **state(game)), 201


@app.get("/api/games/<gid>")
def get_game(gid):
    with LOCK:
        return jsonify(id=gid, **state(find(gid)))


@app.post("/api/games/<gid>/move")
def move(gid):
    data = request.get_json(silent=True) or {}
    try:
        r, c, v = int(data["row"]), int(data["col"]), int(data["value"])
    except (KeyError, TypeError, ValueError):
        raise ValueError("row, col and value (integers) are required")
    with LOCK:
        game = find(gid)
        game.place(r, c, v)
        return jsonify(state(game))


@app.post("/api/games/<gid>/undo")
def undo(gid):
    with LOCK:
        game = find(gid)
        if game.undo() is None:
            raise ValueError("nothing to undo")
        return jsonify(state(game))


@app.post("/api/games/<gid>/redo")
def redo(gid):
    with LOCK:
        game = find(gid)
        if game.redo() is None:
            raise ValueError("nothing to redo")
        return jsonify(state(game))


@app.post("/api/games/<gid>/hint")
def hint(gid):
    with LOCK:
        game = find(gid)
        m = game.hint()
        if m is None:
            raise ValueError("no hint needed")
        return jsonify(**state(game), hint={"row": m.row, "col": m.col, "value": m.new})


@app.get("/api/games/<gid>/check")
def check(gid):
    with LOCK:
        return jsonify(wrong=[[r, c] for r, c in find(gid).wrong_cells()])


@app.post("/api/games/<gid>/solve")
def solve_game(gid):
    with LOCK:
        game = find(gid)
        game.reveal()
        return jsonify(state(game))


@app.get("/api/games/<gid>/analysis")
def analysis(gid):
    with LOCK:
        return jsonify(find(gid).analysis())


@app.get("/api/games/<gid>/history")
def history(gid):
    with LOCK:
        log = find(gid).history.to_list()[-30:]
    return jsonify([{"row": m.row, "col": m.col, "old": m.old, "new": m.new, "kind": m.kind}
                    for m in log])


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)), debug=False)
