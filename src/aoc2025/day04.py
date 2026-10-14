"""Day04: count the paper rolls the Printing Department forklifts can access.

The puzzle input is a rectangular grid of cells where ``@`` marks a paper roll
and ``.`` marks an empty position. A roll is accessible to a forklift when fewer
than four rolls occupy its eight adjacent positions (horizontal, vertical, and
diagonal neighbours). Part 1 counts the rolls accessible in the original grid;
do not implement part 2 until it is authorized.
"""

from collections.abc import Sequence
from pathlib import Path

_ROLL = "@"
_NEIGHBOURS = (-1, 0, 1)


def read_grid(filename: str | Path) -> list[str]:
    """Read a rectangular paper-roll grid from a UTF-8 input file.

    Each nonblank line must contain the same number of characters, and every
    character must be either ``@`` (a roll) or ``.`` (empty). A blank line, a
    line of a different length, or any other character raises ValueError; a
    missing file raises FileNotFoundError.
    """
    if not str(filename):
        raise ValueError("filename must not be empty")
    grid: list[str] = []
    with Path(filename).open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            text = line.strip()
            if not text:
                raise ValueError(f"line {line_number} is blank")
            if any(char not in (_ROLL, ".") for char in text):
                raise ValueError(f"line {line_number} has invalid characters")
            if grid and len(text) != len(grid[0]):
                raise ValueError(f"line {line_number} differs in length")
            grid.append(text)
    return grid


def _roll_is_accessible(grid: Sequence[str], row: int, col: int) -> bool:
    """Return whether the roll at ``grid[row][col]`` has fewer than 4 neighbours."""
    adjacent = 0
    for row_delta in _NEIGHBOURS:
        for col_delta in _NEIGHBOURS:
            if row_delta == 0 and col_delta == 0:
                continue
            neighbour_row = row + row_delta
            neighbour_col = col + col_delta
            if 0 <= neighbour_row < len(grid) and 0 <= neighbour_col < len(grid[0]):
                if grid[neighbour_row][neighbour_col] == _ROLL:
                    adjacent += 1
    return adjacent < 4


def part1(grid: Sequence[str]) -> int:
    """Return the number of rolls accessible to a forklift.

    A roll is accessible when fewer than four rolls occupy its eight adjacent
    positions. Runs in O(R * C) time and O(1) extra space for an ``R``-row,
    ``C``-column grid.
    """
    if not grid:
        return 0
    return sum(
        1
        for row in range(len(grid))
        for col in range(len(grid[0]))
        if grid[row][col] == _ROLL and _roll_is_accessible(grid, row, col)
    )
