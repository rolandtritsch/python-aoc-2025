"""Day07: count how many times a tachyon beam splits in the manifold.

The manifold diagram is a rectangular grid of ``.`` (empty space), ``^``
(splitters), and a single ``S`` (the beam's entry point). A tachyon beam enters
at ``S`` and always moves downward. It passes freely through empty space, but
when it reaches a splitter it is stopped and two new beams continue from the
splitter's immediate left and right, then move downward. Two beams arriving in
the same column merge into one. Part 1 counts every splitter hit, i.e. the total
number of times a beam is split.
"""

from collections.abc import Sequence
from pathlib import Path

_EMPTY = "."
_SPLITTER = "^"
_START = "S"
_VALID_CELLS = frozenset((_EMPTY, _SPLITTER, _START))


def read_grid(filename: str | Path) -> list[str]:
    """Read a manifold diagram file into a list of rows.

    Every nonblank line must hold the same number of characters, each character
    must be ``.``, ``^``, or ``S``, and the diagram must contain exactly one
    ``S`` entry point. A blank line, a ragged row, an invalid character, or a
    missing or duplicated entry point raises ValueError; a missing file raises
    FileNotFoundError.
    """
    if not str(filename):
        raise ValueError("filename must not be empty")
    with Path(filename).open(encoding="utf-8") as source:
        rows = source.read().splitlines()
    if not rows:
        raise ValueError("manifold diagram must not be empty")
    if any(not row for row in rows):
        raise ValueError("manifold diagram must not contain a blank line")
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError("manifold diagram rows must be the same length")
    for line_number, row in enumerate(rows, start=1):
        if any(char not in _VALID_CELLS for char in row):
            raise ValueError(f"line {line_number} contains an invalid character")
    if sum(row.count(_START) for row in rows) != 1:
        raise ValueError("manifold diagram must contain exactly one S")
    return rows


def _entry_column(grid: Sequence[str]) -> int:
    """Return the column index of the single ``S`` entry point."""
    for row in grid:
        if _START in row:
            return row.index(_START)
    raise ValueError("manifold diagram must contain exactly one S")


def part1(grid: Sequence[str]) -> int:
    """Return the number of times the beam is split by the manifold.

    Track the set of beam columns arriving at each row from the row above. A
    beam pulled into a column already occupied by another beam merges with it,
    so a set is exactly right. Each splitter hit increments the total and
    spawns beams one column left and one column right; a beam that leaves the
    grid's left or right edge has exited and is dropped. Runs in O(R * C) time
    and O(C) space for an ``R``-row, ``C``-column grid.
    """
    if not grid:
        return 0
    width = len(grid[0])
    active = {_entry_column(grid)}
    splits = 0
    for row in grid:
        next_active: set[int] = set()
        for column in active:
            if 0 <= column < width and row[column] == _SPLITTER:
                splits += 1
                next_active.add(column - 1)
                next_active.add(column + 1)
            elif 0 <= column < width:
                next_active.add(column)
        active = next_active
    return splits
