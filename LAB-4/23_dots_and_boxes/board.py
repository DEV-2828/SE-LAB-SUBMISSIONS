import copy


class Board:
    def __init__(self, rows=2, cols=2):
        self.rows = rows
        self.cols = cols
        self.horizontal = [[False] * cols for _ in range(rows + 1)]
        self.vertical = [[False] * (cols + 1) for _ in range(rows)]
        self.completed = set()

    # ------------------------------------------------------------------
    # Line placement
    # ------------------------------------------------------------------

    def add_line(self, orientation, row, col):
        if orientation == "H":
            self.horizontal[row][col] = True
        else:
            self.vertical[row][col] = True
        self._update_completed()

    def _update_completed(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if (
                    self.horizontal[r][c]
                    and self.horizontal[r + 1][c]
                    and self.vertical[r][c]
                    and self.vertical[r][c + 1]
                ):
                    self.completed.add((r, c))

    # ------------------------------------------------------------------
    # Undo support — snapshot / restore
    # ------------------------------------------------------------------

    def snapshot(self):
        """Return a deep copy of the board state for undo."""
        return {
            "horizontal": copy.deepcopy(self.horizontal),
            "vertical": copy.deepcopy(self.vertical),
            "completed": set(self.completed),
        }

    def restore(self, snap):
        """Restore board state from a snapshot produced by snapshot()."""
        self.horizontal = copy.deepcopy(snap["horizontal"])
        self.vertical = copy.deepcopy(snap["vertical"])
        self.completed = set(snap["completed"])

    # ------------------------------------------------------------------
    # Game-over check
    # ------------------------------------------------------------------

    def is_complete(self):
        total = (self.rows + 1) * self.cols + self.rows * (self.cols + 1)
        used = sum(map(sum, self.horizontal)) + sum(map(sum, self.vertical))
        return used == total

    # ------------------------------------------------------------------
    # Display
    # ------------------------------------------------------------------

    def display(self, scores, current, move_log=None):
        print()
        print(f"Scores: P1={scores[0]}  P2={scores[1]} | Turn: P{current + 1}")

        for r in range(self.rows + 1):
            print("." + ".".join("---" if self.horizontal[r][c] else "   " for c in range(self.cols)) + ".")
            if r < self.rows:
                middle = []
                for c in range(self.cols + 1):
                    wall = "|" if self.vertical[r][c] else " "
                    middle.append(wall)
                    if c < self.cols:
                        middle.append(" " + ("X" if (r, c) in self.completed else " ") + " ")
                print("".join(middle))
        print()

        if move_log:
            print("  Move history:")
            for entry in move_log:
                print(f"    {entry}")
            print()
