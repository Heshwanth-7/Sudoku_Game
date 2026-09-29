"""Iterative backtracking solver.

* Empty cells are kept in a LinkedList (visited in order, most-constrained first).
* The backtracking path is an explicit Stack instead of recursion.
* The solver returns statistics, which the game uses for puzzle analysis.
"""

import random
from dataclasses import dataclass

from .linked_list import LinkedList
from .stack import Stack

SIZE = 9
BOX = 3


def is_safe(board, r, c, v):
    """True if v can be placed at (r, c) without breaking row/col/box rules."""
    for i in range(SIZE):
        if board[r][i] == v or board[i][c] == v:
            return False
    br, bc = r // BOX * BOX, c // BOX * BOX
    for i in range(br, br + BOX):
        for j in range(bc, bc + BOX):
            if board[i][j] == v:
                return False
    return True


def candidates(board, r, c):
    return [v for v in range(1, SIZE + 1) if is_safe(board, r, c, v)]


@dataclass
class SolveResult:
    solutions: int = 0          # solutions found (capped by `limit`)
    solution: list = None       # first solution found
    steps: int = 0              # digits tried
    backtracks: int = 0         # times we had to undo a placement
    max_depth: int = 0          # deepest the stack grew
    aborted: bool = False       # stopped by max_steps


def solve(board, limit=1, randomize=False, max_steps=None):
    """Solve `board` (0 = empty). The input board is not modified."""
    work = [row[:] for row in board]
    empties = [(r, c) for r in range(SIZE) for c in range(SIZE) if work[r][c] == 0]
    empties.sort(key=lambda rc: len(candidates(work, *rc)))  # most constrained first
    cells = LinkedList(empties)

    orders = {}
    for rc in empties:
        digits = list(range(1, SIZE + 1))
        if randomize:
            random.shuffle(digits)
        orders[rc] = digits

    res = SolveResult()
    stack = Stack()            # holds (list_node, index_of_digit_used)
    node, start = cells.head, 0

    while True:
        if max_steps is not None and res.steps > max_steps:
            res.aborted = True
            break

        if node is None:                       # every cell filled -> a solution
            res.solutions += 1
            if res.solution is None:
                res.solution = [row[:] for row in work]
            if res.solutions >= limit or stack.is_empty():
                break
            node, idx = stack.pop()            # keep searching for more
            r, c = node.data
            work[r][c] = 0
            res.backtracks += 1
            start = idx + 1
            continue

        r, c = node.data
        order = orders[(r, c)]
        placed = False
        for i in range(start, SIZE):
            res.steps += 1
            if is_safe(work, r, c, order[i]):
                work[r][c] = order[i]
                stack.push((node, i))
                res.max_depth = max(res.max_depth, len(stack))
                node, start, placed = node.next, 0, True
                break
        if placed:
            continue

        if stack.is_empty():                   # nothing left to try
            break
        node, idx = stack.pop()                # backtrack
        r, c = node.data
        work[r][c] = 0
        res.backtracks += 1
        start = idx + 1

    return res
