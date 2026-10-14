#!/usr/bin/env python3
"""Independent per-cell reachability reference for AoC 2025 Day07 part1.

A tachyon beam enters the manifold at ``S`` and moves downward. It passes
freely through empty space (``.``) but a splitter (``^``) stops the beam and
emits two new beams from the splitter's immediate left and right, which then
move downward; beams that arrive in the same column merge into one. Part 1
counts every splitter hit.

``src/aoc2025/day07.py`` ``part1`` implements this as a row-by-row column
wavefront: it keeps the set of beam columns active on each row (a set, so
beams in the same column merge automatically), and counts a split whenever an
active column holds a splitter, spawning one column left and one column right
for the next row.

This reference instead tracks individual beam positions as cells and never
forms a per-row column set: a stack of beam cells, a visited-cell set so two
beams arriving at the same cell merge into one, and a splitter cell is counted
the first time a beam reaches it. It shares no helper with ``day07.read_grid``
or ``day07.part1``, so agreement on the sample, the real input, and the
boundary banks is structurally independent acceptance-adjacent evidence for
the merge semantics and the edge drops.

It is a self-checking demonstration for the ``beam-split-cross-check`` skill:
it prints each total and asserts reachability == implementation throughout.
It is read-only against the repository and needs no third-party packages.
"""

from __future__ import annotations

from pathlib import Path

from aoc2025 import day07

REPO_ROOT = Path(__file__).resolve().parents[3]


def reachability_split_count(grid: list[str]) -> int:
    """Return the Day07 part1 split count by explicit per-cell reachability.

    Start from the ``S`` cell. A beam in a cell passes downward: through an
    empty cell it continues straight down; through a splitter it stops, counts
    one split, and two new beams continue from the cells immediately left and
    right below. Beams that leave the grid are dropped, and a cell is visited
    at most once so two beams arriving at the same cell merge into one.
    """
    if not grid:
        return 0
    rows = len(grid)
    cols = len(grid[0])
    entry = None
    for row_index, row in enumerate(grid):
        for col_index, char in enumerate(row):
            if char == "S":
                entry = (row_index, col_index)
                break
        if entry is not None:
            break
    assert entry is not None, "manifold diagram must contain exactly one S"
    visited: set[tuple[int, int]] = set()
    splits = 0
    stack = [entry]
    while stack:
        row, col = stack.pop()
        if not (0 <= row < rows and 0 <= col < cols):
            continue
        if (row, col) in visited:
            continue
        visited.add((row, col))
        if grid[row][col] == "^":
            splits += 1
            stack.append((row + 1, col - 1))
            stack.append((row + 1, col + 1))
        else:
            stack.append((row + 1, col))
    return splits


def cross_check(grid: list[str], expected: int, label: str) -> None:
    """Assert reachability, implementation, and ``expected`` totals agree."""
    reachable = reachability_split_count(grid)
    impl = day07.part1(grid)
    assert reachable == impl == expected, (label, reachable, impl, expected)
    print(f"{label:24s} reachable={reachable} impl={impl}")


def main() -> None:
    sample = day07.read_grid(REPO_ROOT / "inputs" / "Day07Test.txt")
    real = day07.read_grid(REPO_ROOT / "inputs" / "Day07.txt")
    cross_check(sample, 21, "sample")
    cross_check(real, 1605, "real")

    boundaries = {
        "empty": [],
        "single-cell-S": ["S"],
        "straight-down-no-splitter": ["S", ".", ".", "."],
        "single-splitter": ["S", ".", "^"],
        "splitter-off-path": ["S.", ".^"],
        "merged-beams-split-once": [".S.", ".^.", "...", "^.^", "...", ".^.", "..."],
        "left-edge-drops-negative": ["S..", "^..", "..."],
        "right-edge-drops-out-of-range": ["..S", "..^"],
        "adjacent-splitters-spawn-down": [".S..", ".^^.", "....", ".^.^"],
    }
    for name, grid in boundaries.items():
        cross_check(grid, day07.part1(grid), name)

    print(f"boundaries: {len(boundaries)} grids verified")
    print("per-cell reachability == implementation on all checks")


if __name__ == "__main__":
    main()
