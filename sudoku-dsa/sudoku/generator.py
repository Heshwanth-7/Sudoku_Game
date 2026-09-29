"""Puzzle generation: random full grid, then remove cells while keeping a UNIQUE solution."""

import random

from .solver import SIZE, solve

CLUES = {"easy": 40, "medium": 32, "hard": 26}


def generate_solved():
    return solve([[0] * SIZE for _ in range(SIZE)], randomize=True).solution


def generate_puzzle(difficulty="medium"):
    if difficulty not in CLUES:
        raise ValueError(f"difficulty must be one of {list(CLUES)}")
    solution = generate_solved()
    puzzle = [row[:] for row in solution]
    cells = [(r, c) for r in range(SIZE) for c in range(SIZE)]
    random.shuffle(cells)

    clues, target = SIZE * SIZE, CLUES[difficulty]
    for r, c in cells:
        if clues <= target:
            break
        backup, puzzle[r][c] = puzzle[r][c], 0
        res = solve(puzzle, limit=2, max_steps=20000)
        if res.aborted or res.solutions != 1:   # not unique -> put it back
            puzzle[r][c] = backup
        else:
            clues -= 1
    return puzzle, solution
