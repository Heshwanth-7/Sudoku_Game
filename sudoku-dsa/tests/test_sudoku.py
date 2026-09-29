import unittest

from sudoku.game import Game
from sudoku.generator import generate_puzzle
from sudoku.linked_list import LinkedList
from sudoku.solver import solve
from sudoku.stack import Stack

PUZZLE = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0], [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0], [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1], [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0], [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9],
]


def valid_grid(b):
    full = set(range(1, 10))
    rows = all(set(r) == full for r in b)
    cols = all({b[r][c] for r in range(9)} == full for c in range(9))
    boxes = all({b[r][c] for r in range(br, br + 3) for c in range(bc, bc + 3)} == full
                for br in (0, 3, 6) for bc in (0, 3, 6))
    return rows and cols and boxes


class TestStructures(unittest.TestCase):
    def test_linked_list(self):
        ll = LinkedList([1, 2, 3])
        ll.prepend(0)
        self.assertEqual(ll.to_list(), [0, 1, 2, 3])
        self.assertTrue(ll.remove_first(lambda x: x == 3))
        ll.append(9)
        self.assertEqual(ll.to_list(), [0, 1, 2, 9])
        self.assertEqual(ll.pop_front(), 0)
        self.assertEqual(len(ll), 3)

    def test_stack_lifo(self):
        s = Stack()
        for i in range(3):
            s.push(i)
        self.assertEqual((s.peek(), s.pop(), s.pop(), s.pop()), (2, 2, 1, 0))
        self.assertTrue(s.is_empty())
        with self.assertRaises(IndexError):
            s.pop()


class TestSolverAndGame(unittest.TestCase):
    def test_solver_known_puzzle(self):
        res = solve(PUZZLE, limit=2)
        self.assertEqual(res.solutions, 1)
        self.assertTrue(valid_grid(res.solution))
        self.assertEqual(PUZZLE[0][2], 0)  # input untouched

    def test_generated_puzzle_unique(self):
        puzzle, solution = generate_puzzle("easy")
        self.assertTrue(valid_grid(solution))
        self.assertEqual(solve(puzzle, limit=2).solutions, 1)

    def test_undo_redo_and_mistakes(self):
        g = Game(puzzle=PUZZLE)
        right = g.solution[0][2]
        wrong = right % 9 + 1
        g.place(0, 2, wrong)
        self.assertEqual(g.mistakes, 1)
        g.undo()
        self.assertEqual(g.board[0][2], 0)
        g.redo()
        self.assertEqual(g.board[0][2], wrong)
        with self.assertRaises(ValueError):
            g.place(0, 0, 1)  # fixed cell

    def test_full_game_finishes(self):
        g = Game(puzzle=PUZZLE)
        for r in range(9):
            for c in range(9):
                if not g.is_fixed(r, c):
                    g.place(r, c, g.solution[r][c])
        self.assertTrue(g.is_solved())
        self.assertEqual(g.analysis()["mistakes"], 0)


if __name__ == "__main__":
    unittest.main()
