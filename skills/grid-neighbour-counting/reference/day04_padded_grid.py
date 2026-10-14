#!/usr/bin/env python3
"""Independent padded-grid reference for AoC 2025 Day04 part1.

A paper roll (``@``) is accessible to a forklift when fewer than four rolls
occupy its eight adjacent positions. This reference counts accessible rolls by
padding the grid with a border of ``.`` so every original cell has a full
eight-neighbour window with no bounds checks, then applies the statement rule
directly. It cross-checks the repository's bounds-checked implementation on the
official sample, the real input, and boundary grids.

The padded-grid formulation is structurally independent of the implementation
under review: it has no coordinate bounds checks (the border removes them) and
no shared helper, so agreement on the sample, the real input, and the boundary
banks is independent acceptance-adjacent evidence. This is a self-checking
demonstration for the ``grid-neighbour-counting`` skill: it prints each total
and asserts padded == implementation throughout. It is read-only against the
repository and needs no third-party packages.
"""

from __future__ import annotations

from pathlib import Path

from aoc2025 import day04

REPO_ROOT = Path(__file__).resolve().parents[3]

NEIGHBOURS = (-1, 0, 1)


def padded_count(grid: list[str]) -> int:
    """Return the number of accessible rolls using a padded-grid scan.

    Pad the grid with a ``.`` border so each original cell's eight neighbours
    are always in bounds, then apply the statement rule: a roll is accessible
    when fewer than four rolls occupy its adjacent positions.
    """
    if not grid:
        return 0
    pad = ["." + row + "." for row in grid]
    border = "." * len(pad[0])
    pad = [border, *pad, border]
    count = 0
    for row in range(1, len(grid) + 1):
        for col in range(1, len(grid[0]) + 1):
            if pad[row][col] != "@":
                continue
            adjacent = 0
            for row_delta in NEIGHBOURS:
                for col_delta in NEIGHBOURS:
                    if row_delta == 0 and col_delta == 0:
                        continue
                    if pad[row + row_delta][col + col_delta] == "@":
                        adjacent += 1
            if adjacent < 4:
                count += 1
    return count


def main() -> None:
    sample = day04.read_grid(REPO_ROOT / "inputs" / "Day04Test.txt")
    sample_padded = padded_count(sample)
    sample_impl = day04.part1(sample)
    assert sample_padded == sample_impl == 13, (sample_padded, sample_impl)

    real = day04.read_grid(REPO_ROOT / "inputs" / "Day04.txt")
    real_padded = padded_count(real)
    real_impl = day04.part1(real)
    assert real_padded == real_impl == 1356, (real_padded, real_impl)

    boundaries = {
        "empty": [],
        "single": ["@"],
        "full3": ["@@@", "@@@", "@@@"],
        "full4": ["@@@@", "@@@@", "@@@@", "@@@@"],
        "exactly4": [".@.", "@@.", "@@."],
        "diagonal": [".@.", "@.@", ".@."],
        "single-row": ["@@@"],
        "single-col": ["@", "@", "@"],
        "lone-middle": ["...", ".@.", "..."],
        "cross": [".@.", "@@@", ".@."],
    }
    for name, grid in boundaries.items():
        padded = padded_count(grid)
        impl = day04.part1(grid)
        assert padded == impl, (name, padded, impl)

    print(f"sample: padded={sample_padded} impl={sample_impl}")
    print(f"real:   padded={real_padded} impl={real_impl}")
    print(f"boundaries: {len(boundaries)} grids verified")
    print("padded-grid == implementation on all checks")


if __name__ == "__main__":
    main()
