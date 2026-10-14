#!/usr/bin/env python3
"""Independent round-removal reference for AoC 2025 Day04 part2.

A paper roll (``@``) is accessible to a forklift when fewer than four rolls
occupy its eight adjacent positions. Part 2 repeatedly removes accessible rolls
and counts the total removed before none remain. This reference simulates the
statement exactly as its worked example presents it: at each pass, find every
currently accessible roll and remove them all in one synchronous round, then
repeat until no accessible roll remains.

The round-removal formulation is structurally independent of the queue-based
implementation under review (``src/aoc2025/day04.py`` part2): it recomputes
accessibility from scratch each round over the live grid instead of maintaining
per-cell adjacency counts and a removal queue, and it never reuses the
implementation's loops. Because removing a roll only lowers its neighbours'
counts, accessibility is monotone: once a roll is accessible it stays
accessible, so the final removed total is the same whichever order the
accessible rolls are removed in. The synchronous round-removal reference and the
incremental queue cascade must therefore agree on every grid, which makes their
agreement on the real input independent acceptance-adjacent evidence.

This is a self-checking demonstration for the ``grid-neighbour-counting``
skill: it prints each total and asserts round-removal == implementation
throughout. It is read-only against the repository and needs no third-party
packages.
"""

from __future__ import annotations

from pathlib import Path

from aoc2025 import day04

REPO_ROOT = Path(__file__).resolve().parents[3]

NEIGHBOURS = (-1, 0, 1)


def round_removal_count(grid: list[str]) -> int:
    """Return the total rolls removed by synchronous round removal.

    Repeatedly scan the current grid for accessible rolls (fewer than four
    rolls in the eight adjacent positions), remove every such roll in one
    round, and count them. Continue until no roll is accessible. Runs in
    O(R * C * rounds) time and O(R * C) space, which is fine for the small
    grids used as fixtures here.
    """
    if not grid:
        return 0
    rows = len(grid)
    cols = len(grid[0])
    present = [list(row) for row in grid]
    removed = 0
    while True:
        accessible: list[tuple[int, int]] = []
        for row in range(rows):
            for col in range(cols):
                if present[row][col] != "@":
                    continue
                adjacent = 0
                for row_delta in NEIGHBOURS:
                    for col_delta in NEIGHBOURS:
                        if row_delta == 0 and col_delta == 0:
                            continue
                        neighbour_row = row + row_delta
                        neighbour_col = col + col_delta
                        if 0 <= neighbour_row < rows and 0 <= neighbour_col < cols:
                            if present[neighbour_row][neighbour_col] == "@":
                                adjacent += 1
                if adjacent < 4:
                    accessible.append((row, col))
        if not accessible:
            return removed
        removed += len(accessible)
        for row, col in accessible:
            present[row][col] = "."


def main() -> None:
    sample = day04.read_grid(REPO_ROOT / "inputs" / "Day04Test.txt")
    sample_ref = round_removal_count(sample)
    sample_impl = day04.part2(sample)
    assert sample_ref == sample_impl == 43, (sample_ref, sample_impl)

    real = day04.read_grid(REPO_ROOT / "inputs" / "Day04.txt")
    real_ref = round_removal_count(real)
    real_impl = day04.part2(real)
    assert real_ref == real_impl == 8713, (real_ref, real_impl)

    boundaries = {
        "empty": [],
        "single": ["@"],
        "cross": [".@.", "@@@", ".@."],
        "full3": ["@@@", "@@@", "@@@"],
        "full4": ["@@@@", "@@@@", "@@@@", "@@@@"],
        "exactly4": [".@.", "@@.", "@@."],
        "diagonal": [".@.", "@.@", ".@."],
        "single-row": ["@@@"],
        "single-col": ["@", "@", "@"],
        "lone-middle": ["...", ".@.", "..."],
    }
    for name, grid in boundaries.items():
        reference = round_removal_count(grid)
        impl = day04.part2(grid)
        assert reference == impl, (name, reference, impl)

    print(f"sample: round-removal={sample_ref} impl={sample_impl}")
    print(f"real:   round-removal={real_ref} impl={real_impl}")
    print(f"boundaries: {len(boundaries)} grids verified")
    print("round-removal == implementation on all checks")


if __name__ == "__main__":
    main()
