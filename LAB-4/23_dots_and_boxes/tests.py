"""
tests.py — Automated tests for Dots and Boxes.

Covers:
  - valid horizontal move
  - valid vertical move
  - invalid / repeated move
  - completion of a box
  - end-of-game condition
  - configurable board size
  - undo (snapshot / restore)
  - move log display (smoke)
"""

import copy
from board import Board
from rules import valid_move, completed_boxes


# ──────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────

def make_board(rows=2, cols=2):
    return Board(rows=rows, cols=cols)


def _fill_all(board):
    """Fill every line on the board."""
    for r in range(board.rows + 1):
        for c in range(board.cols):
            board.add_line("H", r, c)
    for r in range(board.rows):
        for c in range(board.cols + 1):
            board.add_line("V", r, c)


# ──────────────────────────────────────────────────────────────────────
# Test 1 — Valid horizontal move
# ──────────────────────────────────────────────────────────────────────

def test_valid_horizontal_move():
    b = make_board()
    assert valid_move(b, "H", 0, 0), "H 0 0 should be valid on a fresh board"
    b.add_line("H", 0, 0)
    assert b.horizontal[0][0] is True, "horizontal[0][0] should be True after H 0 0"
    print("PASS  test_valid_horizontal_move")


# ──────────────────────────────────────────────────────────────────────
# Test 2 — Valid vertical move
# ──────────────────────────────────────────────────────────────────────

def test_valid_vertical_move():
    b = make_board()
    assert valid_move(b, "V", 0, 0), "V 0 0 should be valid on a fresh board"
    b.add_line("V", 0, 0)
    assert b.vertical[0][0] is True, "vertical[0][0] should be True after V 0 0"
    print("PASS  test_valid_vertical_move")


# ──────────────────────────────────────────────────────────────────────
# Test 3 — Invalid / repeated move
# ──────────────────────────────────────────────────────────────────────

def test_invalid_move_out_of_bounds():
    b = make_board(rows=2, cols=2)
    # Column 2 does not exist for a 2-col board
    assert not valid_move(b, "H", 0, 2), "H 0 2 must be rejected (out of bounds)"
    assert not valid_move(b, "V", 2, 0), "V 2 0 must be rejected (out of bounds)"
    print("PASS  test_invalid_move_out_of_bounds")


def test_repeated_move():
    b = make_board()
    b.add_line("H", 0, 0)
    # Same move again must be invalid
    assert not valid_move(b, "H", 0, 0), "H 0 0 must be rejected when already placed"
    print("PASS  test_repeated_move")


def test_invalid_orientation():
    b = make_board()
    assert not valid_move(b, "X", 0, 0), "Unknown orientation must be rejected"
    print("PASS  test_invalid_orientation")


# ──────────────────────────────────────────────────────────────────────
# Test 4 — Completion of a box
# ──────────────────────────────────────────────────────────────────────

def test_box_completion():
    b = make_board(rows=2, cols=2)
    moves = [("H", 0, 0), ("H", 1, 0), ("V", 0, 0), ("V", 0, 1)]
    for o, r, c in moves[:-1]:
        before = set(b.completed)
        b.add_line(o, r, c)
        assert completed_boxes(b, before) == 0, f"Box should NOT be complete after {o} {r} {c}"

    # Fourth side closes the box
    before = set(b.completed)
    b.add_line(*moves[-1])
    newly = completed_boxes(b, before)
    assert newly == 1, f"Expected 1 newly completed box, got {newly}"
    assert (0, 0) in b.completed, "Box (0,0) should be in completed set"
    print("PASS  test_box_completion")


def test_double_box_completion():
    """A single move can close two boxes simultaneously (shared edge)."""
    b = make_board(rows=1, cols=2)
    # Box (0,0): needs H[0][0], H[1][0], V[0][0], V[0][1]
    # Box (0,1): needs H[0][1], H[1][1], V[0][1], V[0][2]
    # Shared edge: V[0][1]
    for move in [("H", 0, 0), ("H", 0, 1), ("H", 1, 0), ("H", 1, 1),
                 ("V", 0, 0), ("V", 0, 2)]:
        b.add_line(*move)

    before = set(b.completed)
    b.add_line("V", 0, 1)  # closes both boxes
    newly = completed_boxes(b, before)
    assert newly == 2, f"Expected 2 newly completed boxes, got {newly}"
    print("PASS  test_double_box_completion")


# ──────────────────────────────────────────────────────────────────────
# Test 5 — End-of-game condition
# ──────────────────────────────────────────────────────────────────────

def test_end_of_game():
    b = make_board(rows=2, cols=2)
    assert not b.is_complete(), "Fresh board must not be complete"
    _fill_all(b)
    assert b.is_complete(), "Board with all lines placed must be complete"
    print("PASS  test_end_of_game")


def test_end_of_game_3x3():
    b = make_board(rows=3, cols=3)
    assert not b.is_complete()
    _fill_all(b)
    assert b.is_complete(), "3x3 board with all lines must be complete"
    # All 9 boxes should be claimed
    assert len(b.completed) == 9, f"Expected 9 completed boxes, got {len(b.completed)}"
    print("PASS  test_end_of_game_3x3")


# ──────────────────────────────────────────────────────────────────────
# Test 6 — Configurable board size
# ──────────────────────────────────────────────────────────────────────

def test_configurable_board_size():
    for rows, cols in [(1, 1), (2, 3), (4, 4), (1, 5)]:
        b = Board(rows=rows, cols=cols)
        assert len(b.horizontal) == rows + 1
        assert len(b.horizontal[0]) == cols
        assert len(b.vertical) == rows
        assert len(b.vertical[0]) == cols + 1
    print("PASS  test_configurable_board_size")


# ──────────────────────────────────────────────────────────────────────
# Test 7 — Undo (snapshot / restore)
# ──────────────────────────────────────────────────────────────────────

def test_undo_single_move():
    b = make_board()
    snap = b.snapshot()
    b.add_line("H", 0, 0)
    assert b.horizontal[0][0] is True
    b.restore(snap)
    assert b.horizontal[0][0] is False, "Line should be removed after undo"
    print("PASS  test_undo_single_move")


def test_undo_does_not_share_state():
    """Restoring a snapshot must not mutate it (deep copy safety)."""
    b = make_board()
    snap = b.snapshot()
    b.add_line("H", 0, 0)
    b.restore(snap)
    # Mutate again after restore — snap should stay pristine
    b.add_line("V", 0, 0)
    b.restore(snap)
    assert b.vertical[0][0] is False, "Snapshot must not be affected by later changes"
    print("PASS  test_undo_does_not_share_state")


def test_undo_after_box_completion():
    b = make_board()
    for move in [("H", 0, 0), ("H", 1, 0), ("V", 0, 0)]:
        b.add_line(*move)
    snap = b.snapshot()
    b.add_line("V", 0, 1)  # closes box
    assert (0, 0) in b.completed
    b.restore(snap)
    assert (0, 0) not in b.completed, "Completed box must be removed after undo"
    print("PASS  test_undo_after_box_completion")


# ──────────────────────────────────────────────────────────────────────
# Test 8 — Move log display (smoke test)
# ──────────────────────────────────────────────────────────────────────

def test_move_log_display_smoke():
    import io, sys
    b = make_board()
    b.add_line("H", 0, 0)
    log = ["P1: H 0 0"]
    captured = io.StringIO()
    sys.stdout = captured
    b.display([0, 0], 1, move_log=log)
    sys.stdout = sys.__stdout__
    output = captured.getvalue()
    assert "Move history" in output, "Move history header not found in display output"
    assert "P1: H 0 0" in output, "Move log entry not found in display output"
    print("PASS  test_move_log_display_smoke")


# ──────────────────────────────────────────────────────────────────────
# Runner
# ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    tests = [
        test_valid_horizontal_move,
        test_valid_vertical_move,
        test_invalid_move_out_of_bounds,
        test_repeated_move,
        test_invalid_orientation,
        test_box_completion,
        test_double_box_completion,
        test_end_of_game,
        test_end_of_game_3x3,
        test_configurable_board_size,
        test_undo_single_move,
        test_undo_does_not_share_state,
        test_undo_after_box_completion,
        test_move_log_display_smoke,
    ]

    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            print(f"FAIL  {t.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR {t.__name__}: {e}")
            failed += 1

    print(f"\n{'='*40}")
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    if failed == 0:
        print("All tests passed! OK")
