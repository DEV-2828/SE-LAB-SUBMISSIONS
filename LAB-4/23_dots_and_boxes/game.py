from board import Board
from rules import valid_move, completed_boxes


class DotsAndBoxes:
    def __init__(self):
        rows, cols = self._ask_board_size()
        self.board = Board(rows=rows, cols=cols)
        self.current = 0
        self.scores = [0, 0]
        self.move_log = []        # Feature: move history
        self._history = []        # Feature: undo stack  [(snap, player, scores_snap)]

    # ------------------------------------------------------------------
    # Setup helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _ask_board_size():
        """Prompt for board dimensions; fall back to 2x2 on bad input."""
        print("\n=== Dots and Boxes ===")
        print("Board size (rows x cols). Press Enter for default 2x2.")
        raw = input("Enter rows cols (e.g. 3 3): ").strip()
        if not raw:
            return 2, 2
        parts = raw.split()
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            r, c = int(parts[0]), int(parts[1])
            if 1 <= r <= 9 and 1 <= c <= 9:
                return r, c
        print("Invalid size — using default 2x2.")
        return 2, 2

    # ------------------------------------------------------------------
    # Main game loop
    # ------------------------------------------------------------------

    def run(self):
        print(f"\nBoard: {self.board.rows}x{self.board.cols} "
              f"({self.board.rows * self.board.cols} boxes total)")
        print("Commands: H row col | V row col | UNDO")
        print("Rows and columns start at 0.")
        print("Example: H 0 1")

        while not self.board.is_complete():
            self.board.display(self.scores, self.current)
            raw = input(f"Player {self.current + 1}, move: ").strip().upper()

            # ---- UNDO command ----------------------------------------
            if raw == "UNDO":
                self._handle_undo()
                continue

            parts = raw.split()

            if len(parts) != 3:
                print("Invalid format. Use: H row col | V row col | UNDO")
                continue

            orientation, row, col = parts
            if not row.isdigit() or not col.isdigit():
                print("Row and column must be non-negative integers.")
                continue

            row, col = int(row), int(col)
            if not valid_move(self.board, orientation, row, col):
                print("Invalid or already-used move.")
                continue

            # ---- Record snapshot for undo BEFORE applying the move ---
            self._history.append({
                "board_snap": self.board.snapshot(),
                "player": self.current,
                "scores": list(self.scores),
                "log_len": len(self.move_log),
            })

            # ---- Apply the move --------------------------------------
            before = set(self.board.completed)
            self.board.add_line(orientation, row, col)
            newly_completed = completed_boxes(self.board, before)

            # ---- Log the move ----------------------------------------
            tag = f"P{self.current + 1}: {orientation} {row} {col}"
            if newly_completed:
                tag += f"  (+{newly_completed} box{'es' if newly_completed > 1 else ''})"
            self.move_log.append(tag)

            # ---- Update score / turn ---------------------------------
            if newly_completed:
                self.scores[self.current] += newly_completed
                print(f"Player {self.current + 1} completed {newly_completed} "
                      f"box(es) and plays again.")
            else:
                self.current = 1 - self.current

        # ---- Game over -----------------------------------------------
        self.board.display(self.scores, self.current, move_log=self.move_log)
        print("Game over!")
        if self.scores[0] == self.scores[1]:
            print("The game is a draw.")
        else:
            winner = 1 if self.scores[0] > self.scores[1] else 2
            print(f"Player {winner} wins!")

    # ------------------------------------------------------------------
    # Undo handler
    # ------------------------------------------------------------------

    def _handle_undo(self):
        if not self._history:
            print("Nothing to undo.")
            return
        snap = self._history.pop()
        self.board.restore(snap["board_snap"])
        self.current = snap["player"]
        self.scores = snap["scores"]
        # Trim move log back to length before the undone move
        del self.move_log[snap["log_len"]:]
        print("Last move undone.")
