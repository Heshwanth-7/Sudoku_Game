"""Game logic.

Data structures used:
  undo_stack / redo_stack : Stack       -> unlimited undo / redo
  history                 : LinkedList  -> chronological log of every action
  hint pool               : LinkedList  -> cells that are still empty/wrong
"""

import random
import time
from dataclasses import dataclass

from .generator import generate_puzzle
from .linked_list import LinkedList
from .solver import SIZE, is_safe, solve
from .stack import Stack


@dataclass(frozen=True)
class Move:
    row: int
    col: int
    old: int
    new: int
    kind: str = "move"   # move | hint | undo | redo


class Game:
    def __init__(self, difficulty="medium", puzzle=None):
        self.difficulty = difficulty
        if puzzle is None:
            puzzle, solution = generate_puzzle(difficulty)
        else:
            res = solve(puzzle)
            if res.solution is None:
                raise ValueError("puzzle has no solution")
            solution = res.solution
        self.puzzle = puzzle
        self.solution = solution
        self.board = [row[:] for row in puzzle]

        self.undo_stack = Stack()
        self.redo_stack = Stack()
        self.history = LinkedList()

        self.moves = self.mistakes = self.hints = self.undos = 0
        self.started = time.time()
        self.finished = None
        self.revealed = False

        # analysis of the puzzle itself (how hard is it for a backtracking solver?)
        self.puzzle_stats = solve(puzzle, limit=2)

    # ---------- queries ----------
    def is_fixed(self, r, c):
        return self.puzzle[r][c] != 0

    def is_solved(self):
        return self.board == self.solution

    def elapsed(self):
        return (self.finished or time.time()) - self.started

    def wrong_cells(self):
        return [(r, c) for r in range(SIZE) for c in range(SIZE)
                if self.board[r][c] and self.board[r][c] != self.solution[r][c]]

    def has_conflict(self, r, c):
        v = self.board[r][c]
        if v == 0:
            return False
        self.board[r][c] = 0
        ok = is_safe(self.board, r, c, v)
        self.board[r][c] = v
        return not ok

    # ---------- actions ----------
    def _apply(self, move):
        self.board[move.row][move.col] = move.new
        self.history.append(move)
        if self.is_solved() and self.finished is None:
            self.finished = time.time()

    def place(self, r, c, v):
        if not (0 <= r < SIZE and 0 <= c < SIZE and 0 <= v <= SIZE):
            raise ValueError("row, column and value must be within range")
        if self.is_fixed(r, c):
            raise ValueError("that cell is part of the puzzle and cannot be changed")
        if self.board[r][c] == v:
            raise ValueError("cell already has that value")
        move = Move(r, c, self.board[r][c], v)
        self._apply(move)
        self.undo_stack.push(move)
        self.redo_stack.clear()
        self.moves += 1
        if v != 0 and v != self.solution[r][c]:
            self.mistakes += 1
        return move

    def undo(self):
        if self.undo_stack.is_empty():
            return None
        m = self.undo_stack.pop()
        self.redo_stack.push(m)
        self.undos += 1
        self.finished = None
        self._apply(Move(m.row, m.col, m.new, m.old, "undo"))
        return m

    def redo(self):
        if self.redo_stack.is_empty():
            return None
        m = self.redo_stack.pop()
        self.undo_stack.push(m)
        self._apply(Move(m.row, m.col, m.old, m.new, "redo"))
        return m

    def hint(self):
        pool = LinkedList((r, c) for r in range(SIZE) for c in range(SIZE)
                          if self.board[r][c] != self.solution[r][c])
        if pool.is_empty():
            return None
        r, c = random.choice(pool.to_list())
        move = Move(r, c, self.board[r][c], self.solution[r][c], "hint")
        self._apply(move)
        self.undo_stack.push(move)
        self.redo_stack.clear()
        self.hints += 1
        return move

    def reveal(self):
        self.board = [row[:] for row in self.solution]
        self.revealed = True
        self.finished = self.finished or time.time()

    # ---------- analysis ----------
    def analysis(self):
        filled = sum(1 for r in range(SIZE) for c in range(SIZE)
                     if self.board[r][c] and not self.is_fixed(r, c))
        to_fill = sum(1 for row in self.puzzle for v in row if v == 0)
        s = self.puzzle_stats
        accuracy = 100.0 if self.moves == 0 else 100.0 * (self.moves - self.mistakes) / self.moves
        score = max(0, 1000 - 25 * self.mistakes - 50 * self.hints - int(self.elapsed() // 10))
        return {
            "difficulty": self.difficulty,
            "clues given": SIZE * SIZE - to_fill,
            "progress": f"{filled}/{to_fill} cells ({100 * filled // to_fill}%)",
            "time": f"{int(self.elapsed() // 60)}m {int(self.elapsed() % 60)}s",
            "moves": self.moves,
            "mistakes": self.mistakes,
            "accuracy": f"{accuracy:.0f}%",
            "hints used": self.hints,
            "undos": self.undos,
            "unique solution": "yes" if s.solutions == 1 else "no",
            "solver steps": s.steps,
            "solver backtracks": s.backtracks,
            "solver max stack depth": s.max_depth,
            "score": score,
        }
