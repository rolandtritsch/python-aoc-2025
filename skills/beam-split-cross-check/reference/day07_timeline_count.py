#!/usr/bin/env python3
"""Independent many-worlds timeline-count reference for AoC 2025 Day07 part2.

Day07 part2 sends one quantum tachyon particle that takes both the left and
right branch of every splitter: each time a particle reaches a splitter, time
itself splits into one timeline that went left and one that went right. Two
timelines are distinct even when they reach the same cell, because they
arrived along different histories; the answer counts every completed journey.

``src/aoc2025/day07.py`` ``part2`` computes this as a top-down row wavefront
of per-column timeline counts: a dict maps each column to how many timelines
are currently at that column, a splitter column sends its count one column
left and right, an empty column continues it straight down, and a timeline
that leaves the left/right edge or the bottom is counted exactly once. The
counts are added when timelines coincide, never deduplicated, which is exactly
the "timelines stay distinct" semantics.

This reference verifies that total two independent ways:

- ``enumerate_timeline_count`` brute-force walks every distinct timeline as an
  explicit path of cells (forking at each splitter, counting once when the
  path leaves the grid). It is the many-worlds definition directly, shares no
  aggregation shortcut with the implementation, and never merges coinciding
  paths, so it is a check that the implementation's per-column counts really
  count distinct journeys rather than merged ones. It is tractable on the
  official sample (40 timelines) and the boundary banks but not on the real
  input (29893386035180 distinct timelines).
- ``memo_timeline_count`` computes the same total with a bottom-up recursion
  over cells ``count(row, col)``: an exited cell contributes 1, a splitter
  sums its two children, and any other cell continues one row down. It shares
  no helper and no data flow with the top-down row wavefront (it has no
  per-row dict and no running accumulator), so agreement on the real input is
  structural, not a transcription.

It is a self-checking demonstration for the ``beam-split-cross-check`` skill:
it prints each total and asserts the references equal the implementation on
the sample, the real input, and the boundary banks. It is read-only against
the repository and needs no third-party packages.
"""

from __future__ import annotations

from functools import cache
from pathlib import Path

from aoc2025 import day07

REPO_ROOT = Path(__file__).resolve().parents[3]


def _entry(grid: list[str]) -> tuple[int, int]:
    """Return the (row, col) of the single ``S`` entry point."""
    for row_index, row in enumerate(grid):
        for col_index, char in enumerate(row):
            if char == "S":
                return (row_index, col_index)
    raise AssertionError("manifold diagram must contain exactly one S")


def enumerate_timeline_count(grid: list[str]) -> int:
    """Return the Day07 part2 timeline count by explicit path enumeration.

    Walk every distinct timeline as an explicit sequence of cells. An
    out-of-grid cell is one completed journey; a splitter cell forks the
    journey into the cell immediately left and right one row down; any other
    cell continues one row down. Coinciding paths are never merged, so the
    number of stack entries is the number of distinct timelines.
    """
    if not grid:
        return 0
    rows = len(grid)
    cols = len(grid[0])
    completed = 0
    stack: list[tuple[int, int]] = [_entry(grid)]
    while stack:
        row, col = stack.pop()
        if not (0 <= row < rows and 0 <= col < cols):
            completed += 1
        elif grid[row][col] == "^":
            stack.append((row + 1, col - 1))
            stack.append((row + 1, col + 1))
        else:
            stack.append((row + 1, col))
    return completed


def memo_timeline_count(grid: list[str]) -> int:
    """Return the Day07 part2 timeline count with bottom-up cell recursion.

    ``count(row, col)`` is the number of completed timelines a particle can
    produce from that cell: an exited cell contributes 1, a splitter sums its
    two children (each timeline forks), and any other cell continues one row
    down. The grid is acyclic (only downward moves), so the memoized
    recurrence terminates. Never merges coinciding timelines.
    """
    if not grid:
        return 0
    rows = len(grid)
    cols = len(grid[0])

    @cache
    def count(row: int, col: int) -> int:
        if not (0 <= row < rows and 0 <= col < cols):
            return 1
        if grid[row][col] == "^":
            return count(row + 1, col - 1) + count(row + 1, col + 1)
        return count(row + 1, col)

    entry_row, entry_col = _entry(grid)
    return count(entry_row, entry_col)


def cross_check(grid: list[str], expected: int, label: str) -> None:
    """Assert both references and the implementation agree with ``expected``."""
    enumerated = enumerate_timeline_count(grid)
    memoized = memo_timeline_count(grid)
    impl = day07.part2(grid)
    assert enumerated == memoized == impl == expected, (
        label,
        enumerated,
        memoized,
        impl,
        expected,
    )
    print(f"{label:30s} enumerated={enumerated} memo={memoized} impl={impl}")


def main() -> None:
    sample = day07.read_grid(REPO_ROOT / "inputs" / "Day07Test.txt")
    real = day07.read_grid(REPO_ROOT / "inputs" / "Day07.txt")
    cross_check(sample, 40, "sample")
    memoized = memo_timeline_count(real)
    impl = day07.part2(real)
    assert memoized == impl == 29893386035180, (memoized, impl)
    print(f"{'real':30s} enumerated=intractable memo={memoized} impl={impl}")

    boundaries = {
        "empty": [],
        "single-cell-S": ["S"],
        "straight-down-no-splitter": ["S", ".", ".", "."],
        "single-splitter": ["S", ".", "^"],
        "splitter-off-path": ["S.", ".^"],
        "converging-timelines-stay-distinct": [
            "...S...",
            "...^...",
            "..^.^..",
            ".......",
        ],
        "coincide-at-splitter-stay-distinct": [
            "...S...",
            "...^...",
            "..^.^..",
            "...^...",
            ".......",
        ],
        "left-edge-drops-negative": ["S..", "^..", "..."],
        "right-edge-drops-out-of-range": ["..S", "..^"],
        "last-row-splitter-exits": [".S", ".^"],
    }
    for name, grid in boundaries.items():
        cross_check(grid, day07.part2(grid), name)

    print(f"boundaries: {len(boundaries)} grids verified")
    print("enumerated == memo == implementation on all checks")


if __name__ == "__main__":
    main()
