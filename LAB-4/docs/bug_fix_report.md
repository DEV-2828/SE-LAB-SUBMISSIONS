# Bug Fix Report — Dots and Boxes

**Project:** `23_dots_and_boxes`  
**Files Analyzed:** `board.py`, `game.py`, `rules.py`, `main.py`  
**Total Bugs Found & Fixed:** 2

---

## Bug #1 — Board Display: Missing Outer Dots on Every Row

**File:** [`board.py`](file:///c:/DEVOPAM/ENGINEERING/SEM-5/3_Software_engineering/SE_LAB/LAB-4/23_dots_and_boxes/board.py) — Line 37  
**Severity:** 🔴 High — Visual corruption on every printed board state

### What Was Wrong

In Dots and Boxes, every horizontal row of dots must start and end with a dot (`.`), with line segments (`---`) or gaps (`   `) between them.

For a 2×2 board, each row must look like:

```
.   .   .      (all gaps — initial state)
.---.---.      (all filled)
.---.   .      (partially filled)
```

However, the original `display()` method used Python's `str.join()` directly on the list of segments:

```python
# BUG: ".".join(...) produces "seg0.seg1" — missing leading and trailing dot
print(".".join("---" if self.horizontal[r][c] else "   " for c in range(self.cols)))
```

`str.join()` only places a separator *between* items — it never adds leading or trailing separators. So for 2 segments, only **1 dot** was produced instead of **3**.

### Code That Caused It

```python
# board.py — line 37 (BEFORE FIX)
print(".".join("---" if self.horizontal[r][c] else "   " for c in range(self.cols)))
```

### Fix Applied

```python
# board.py — line 37 (AFTER FIX)
print("." + ".".join("---" if self.horizontal[r][c] else "   " for c in range(self.cols)) + ".")
```

By prepending and appending a `"."` to the joined string, the leading and trailing dots are correctly rendered.

### Before vs After Expected Output

**Before (2×2 board, initial state):**
```
   .   
```
*(Only 1 dot instead of 3; missing left and right boundary dots)*

**After (2×2 board, initial state):**
```
.   .   .
```
*(Correct: 3 dots with 2 empty segments between them)*

**Before (fully filled row):**
```
---.---
```
*(Missing boundary dots)*

**After (fully filled row):**
```
.---.---.
```
*(Correct: dots at both ends)*

---

## Bug #2 — Board Display: Missing Outer Dots Causes Misaligned Vertical Row

**File:** [`board.py`](file:///c:/DEVOPAM/ENGINEERING/SEM-5/3_Software_engineering/SE_LAB/LAB-4/23_dots_and_boxes/board.py) — Line 37 (same root cause as Bug #1)  
**Severity:** 🟠 Medium — Structural misalignment between dot rows and vertical rows

### What Was Wrong

The vertical (middle) rows print correctly: `| X |` or `|   |`, with exactly the right number of walls and cell markers. However, because the horizontal rows were missing their leading dot, the columns did not visually align.

A correct 2×2 mid-game board should look like:

```
.---.---.
|   | X |
.---.---.
|   |   |
.   .   .
```

But before the fix it looked like:

```
---.---
|   | X |
---.---
|   |   |
   .   
```

The horizontal rows were shifted left by one character (the missing leading dot), making walls appear to not align with the dots above/below them.

### Code That Caused It

Same as Bug #1 — the missing `"."` prefix in line 37.

### Fix Applied

Same fix as Bug #1 — prepend and append `"."` to the joined string.

### Before vs After Expected Output

**Before:**
```
---.---
|   |
   .   
```

**After:**
```
.---.---.
|   |   |
.   .   .
```

---

## Summary Table

| # | File | Line | Bug | Fix |
|---|------|------|-----|-----|
| 1 | `board.py` | 37 | `".".join(...)` missing leading dot | Prepend `"."` to the joined string |
| 2 | `board.py` | 37 | Same root cause — misaligned column display | Same fix — append `"."` to the joined string |

---

## Full Diff of Changes

```diff
--- a/board.py
+++ b/board.py
@@ -34,7 +34,7 @@ class Board:
         for r in range(self.rows + 1):
-            print(".".join("---" if self.horizontal[r][c] else "   " for c in range(self.cols)))
+            print("." + ".".join("---" if self.horizontal[r][c] else "   " for c in range(self.cols)) + ".")
             if r < self.rows:
```

---

## User-Reported Issue Analysis

The user reported `H 2 2` being rejected as "Invalid or already-used move" and suspected a bug. This is **correct behavior**:

- The board is 2×2, meaning horizontal columns are indexed `0` and `1` only (range `[0, cols)`).
- `H 2 2` specifies column `2`, which is **out of bounds** for a 2-column board.
- `rules.py`'s `valid_move()` correctly rejects this: `0 <= col < board.cols` → `0 <= 2 < 2` → `False`.
- **No bug here** — the validation is working as intended.

---

## Files Changed

- [`board.py`](file:///c:/DEVOPAM/ENGINEERING/SEM-5/3_Software_engineering/SE_LAB/LAB-4/23_dots_and_boxes/board.py) — Line 37 (display fix)
