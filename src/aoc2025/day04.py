"""Day04: count the paper rolls the Printing Department forklifts can access.

The puzzle input is a rectangular grid of cells where ``@`` marks a paper roll
and ``.`` marks an empty position. A roll is accessible to a forklift when fewer
than four rolls occupy its eight adjacent positions (horizontal, vertical, and
diagonal neighbours). Part 1 counts the rolls accessible in the original grid.
Part 2 repeatedly removes accessible rolls (each removal can unlock further
rolls) and counts the total removed before no accessible roll remains.
"""

from collections import deque
from collections.abc import Sequence
from pathlib import Path

_ROLL = "@"
_NEIGHBOURS = (-1, 0, 1)
_ACCESSIBLE_MAX_NEIGHBOURS = 3


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
    return adjacent <= _ACCESSIBLE_MAX_NEIGHBOURS


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


def part2(grid: Sequence[str]) -> int:
    """Return the total rolls removable by repeated access and removal.

    Removing a roll can only lower its neighbours' adjacency counts, so an
    accessible roll never becomes inaccessible later: the cascade is monotone
    and the final total is independent of removal order. Simulate it with a
    queue of accessible rolls. First count each roll's neighbours, seed the
    queue with every roll that has fewer than four, then pop one roll at a time,
    decrement the neighbours of its still-present adjacent rolls, and queue any
    that drop below four. Runs in O(R * C) time and O(R * C) space for an
    ``R``-row, ``C``-column grid.
    """
    if not grid:
        return 0
    rows = len(grid)
    cols = len(grid[0])
    present = [[cell == _ROLL for cell in row] for row in grid]
    adjacent = [[0] * cols for _ in range(rows)]
    for row in range(rows):
        for col in range(cols):
            if not present[row][col]:
                continue
            count = 0
            for row_delta in _NEIGHBOURS:
                for col_delta in _NEIGHBOURS:
                    if row_delta == 0 and col_delta == 0:
                        continue
                    neighbour_row = row + row_delta
                    neighbour_col = col + col_delta
                    if 0 <= neighbour_row < rows and 0 <= neighbour_col < cols:
                        if present[neighbour_row][neighbour_col]:
                            count += 1
            adjacent[row][col] = count

    queue = deque(
        (row, col)
        for row in range(rows)
        for col in range(cols)
        if present[row][col] and adjacent[row][col] <= _ACCESSIBLE_MAX_NEIGHBOURS
    )
    removed = 0
    while queue:
        row, col = queue.popleft()
        if not present[row][col]:
            continue
        present[row][col] = False
        removed += 1
        for row_delta in _NEIGHBOURS:
            for col_delta in _NEIGHBOURS:
                if row_delta == 0 and col_delta == 0:
                    continue
                neighbour_row = row + row_delta
                neighbour_col = col + col_delta
                if 0 <= neighbour_row < rows and 0 <= neighbour_col < cols:
                    if present[neighbour_row][neighbour_col]:
                        adjacent[neighbour_row][neighbour_col] -= 1
                        if (
                            adjacent[neighbour_row][neighbour_col]
                            <= _ACCESSIBLE_MAX_NEIGHBOURS
                        ):
                            queue.append((neighbour_row, neighbour_col))
    return removed
