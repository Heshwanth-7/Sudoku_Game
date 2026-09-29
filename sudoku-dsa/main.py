"""Console Sudoku. Run:  python main.py [easy|medium|hard]"""

import sys

from sudoku.game import Game
from sudoku.generator import CLUES

BOLD, CYAN, RED, RESET = "\033[1m", "\033[36m", "\033[31m", "\033[0m"
USE_COLOR = sys.stdout.isatty()

HELP = """Commands (rows/columns/values are 1-9):
  r c v          place value v at row r, column c        e.g.  3 4 7
  clear r c      empty a cell                            e.g.  clear 3 4
  undo / redo    step back / forward (stack based)
  hint           fill one correct cell (costs score)
  check          list wrong or conflicting cells
  analysis       show statistics about you and the puzzle
  history [n]    show the last n actions (linked list log)
  solve          give up and reveal the solution
  new [level]    new game: easy | medium | hard
  help, quit"""


def paint(text, code):
    return f"{code}{text}{RESET}" if USE_COLOR else text


def render(game):
    border = "  +" + ("-" * 7 + "+") * 3
    header = "   " + "  ".join(" " + " ".join(str(c + 1) for c in range(g, g + 3))
                              for g in (0, 3, 6))
    out = [header, border]
    for r in range(9):
        row = f"{r + 1} |"
        for c in range(9):
            v = game.board[r][c]
            ch = "." if v == 0 else str(v)
            if v and game.is_fixed(r, c):
                ch = paint(ch, BOLD)
            elif v and game.has_conflict(r, c):
                ch = paint(ch, RED)
            elif v:
                ch = paint(ch, CYAN)
            row += " " + ch
            if c % 3 == 2:
                row += " |"
        out.append(row)
        if r % 3 == 2:
            out.append(border)
    return "\n".join(out)


def show_analysis(game):
    print("\n--- Analysis ---")
    for k, v in game.analysis().items():
        print(f"  {k:<24}{v}")
    print()


def describe(m):
    val = m.new if m.new else "empty"
    return f"{m.kind:<5} r{m.row + 1} c{m.col + 1}: {m.old or 'empty'} -> {val}"


def new_game(level):
    print(f"Generating a {level} puzzle...")
    return Game(level)


def main():
    level = sys.argv[1].lower() if len(sys.argv) > 1 else "medium"
    if level not in CLUES:
        sys.exit(f"Level must be one of: {', '.join(CLUES)}")
    game = new_game(level)
    print(HELP)

    while True:
        print("\n" + render(game))
        if game.is_solved():
            print("\nSolved! Congratulations!")
            show_analysis(game)
            if input("Play again? (y/n) ").strip().lower().startswith("y"):
                game = new_game(level)
                continue
            return
        try:
            line = input("\n> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        parts = line.split()
        if not parts:
            continue
        cmd = parts[0]
        try:
            if cmd in ("quit", "exit", "q"):
                return
            elif cmd == "help":
                print(HELP)
            elif cmd == "undo":
                m = game.undo()
                print("Undid: " + describe(m) if m else "Nothing to undo.")
            elif cmd == "redo":
                m = game.redo()
                print("Redid: " + describe(m) if m else "Nothing to redo.")
            elif cmd == "hint":
                m = game.hint()
                print(f"Hint: row {m.row + 1}, col {m.col + 1} = {m.new}" if m else "No hints needed.")
            elif cmd == "check":
                wrong = game.wrong_cells()
                if wrong:
                    print("Wrong cells: " + ", ".join(f"(r{r + 1},c{c + 1})" for r, c in wrong))
                else:
                    print("All filled cells are correct so far.")
            elif cmd == "analysis":
                show_analysis(game)
            elif cmd == "history":
                n = int(parts[1]) if len(parts) > 1 else 10
                log = game.history.to_list()[-n:]
                print("\n".join(describe(m) for m in log) or "No actions yet.")
            elif cmd == "solve":
                game.reveal()
                print(render(game))
                show_analysis(game)
                return
            elif cmd == "new":
                if len(parts) > 1:
                    if parts[1] not in CLUES:
                        raise ValueError(f"level must be one of {list(CLUES)}")
                    level = parts[1]
                game = new_game(level)
            elif cmd == "clear" and len(parts) == 3:
                game.place(int(parts[1]) - 1, int(parts[2]) - 1, 0)
            elif len(parts) == 3 and all(p.isdigit() for p in parts):
                r, c, v = (int(p) for p in parts)
                if v == 0:
                    raise ValueError("use 'clear r c' to empty a cell")
                game.place(r - 1, c - 1, v)
                if game.has_conflict(r - 1, c - 1):
                    print("Warning: that number conflicts with its row, column or box.")
            else:
                print("Unknown command. Type 'help'.")
        except ValueError as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
