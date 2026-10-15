#!/usr/bin/env python3
"""Independent loop-fill + rectangle reference for AoC 2025 Day09 part2.

The Elves fill in the green tiles: every red tile connects to the red tile
before and after it by a straight line of green tiles (the list wraps, and
adjacent tiles are on the same row or column), and all tiles inside this loop
are green too. Part 2 asks for the largest rectangle whose opposite corners
are red tiles and whose every other tile is red or green. The official sample
gives 24 (between ``9,5`` and ``2,3``); the real input gives ``1439894345``.

``src/aoc2025/day09.py`` ``_filled_regions`` builds the loop's vertical and
horizontal edges, computes per-row red/green ``(x_lo, x_hi)`` intervals with an
even-odd scanline over half-open ``[y_lo, y_hi)`` walls plus re-added horizontal
edges, merges adjacent intervals, compresses identical consecutive rows, and
``_covers`` decides rectangle coverage with a ``bisect_right`` lookup.
``part2`` then evaluates every red-tile pair, pruning on area.

This reference is structurally independent of that implementation:

- It never builds edges, never applies an even-odd scanline, never merges
  intervals, and never calls ``bisect``.
- ``boundary_cells`` walks each tile-to-tile run and emits the explicit cell
  positions on the loop.
- ``filled_cells`` adds the interior by flood-filling the *exterior* of a
  padded grid and marking every non-exterior cell, a per-cell reachability
  computation with no interval arithmetic.
- ``largest_rect`` checks every red-tile pair by per-cell set membership over
  the rectangle's actual cells, with an area-pruning guard.

It is a self-checking demonstration for the ``loop-fill-rectangle-cross-check``
skill: it prints the totals and asserts the reference equals the implementation
on the official sample, the boundary banks, and a corpus of small orthogonal
loops, and on the real input it independently verifies the *filled volume* with
Pick's theorem plus the shoelace formula (no cell enumeration) and reports the
rectangle total reproduced by the implementation. It is read-only against the
repository and needs no third-party packages.
"""

from __future__ import annotations

from collections import deque
from pathlib import Path

from aoc2025 import day09
from aoc2025.day09 import Tile

REPO_ROOT = Path(__file__).resolve().parents[3]


def boundary_cells(tiles: list[Tile]) -> set[tuple[int, int]]:
    """Return the set of cells on the loop boundary.

    Each consecutive tile pair (with the list wrapping) is joined by a straight
    run on a shared row or column; every cell on that run is on the boundary.
    """
    boundary: set[tuple[int, int]] = set()
    for i in range(len(tiles)):
        a = tiles[i]
        b = tiles[(i + 1) % len(tiles)]
        if a.x == b.x:
            for y in range(min(a.y, b.y), max(a.y, b.y) + 1):
                boundary.add((a.x, y))
        else:
            for x in range(min(a.x, b.x), max(a.x, b.x) + 1):
                boundary.add((x, a.y))
    return boundary


def filled_cells(tiles: list[Tile]) -> set[tuple[int, int]]:
    """Return the red/green cells: the boundary plus the loop's interior.

    The interior is found by flood-filling the exterior of the bounding box
    (padded by one cell on every side) starting from the padded corner: every
    cell reachable from outside without crossing the boundary is exterior, so
    every cell that is not boundary and not exterior lies inside the loop.
    """
    boundary = boundary_cells(tiles)
    x_min = min(t.x for t in tiles) - 1
    x_max = max(t.x for t in tiles) + 1
    y_min = min(t.y for t in tiles) - 1
    y_max = max(t.y for t in tiles) + 1
    outside: set[tuple[int, int]] = set()
    queue: deque[tuple[int, int]] = deque()
    queue.append((x_min, y_min))
    outside.add((x_min, y_min))
    while queue:
        x, y = queue.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if not (x_min <= nx <= x_max and y_min <= ny <= y_max):
                continue
            if (nx, ny) in outside or (nx, ny) in boundary:
                continue
            outside.add((nx, ny))
            queue.append((nx, ny))
    filled = set(boundary)
    for y in range(y_min + 1, y_max):
        for x in range(x_min + 1, x_max):
            if (x, y) not in outside:
                filled.add((x, y))
    return filled


def largest_rect(tiles: list[Tile]) -> int:
    """Return the largest red-cornered rectangle whose cells are all red/green.

    Every red-tile pair is treated as opposite corners; a rectangle is valid
    when each of its cells is in the per-cell filled set. Pairs whose area is
    no larger than the best found so far are skipped. Rejects fewer than two
    tiles.
    """
    if len(tiles) < 2:
        raise ValueError("at least two tiles are required")
    filled = filled_cells(tiles)
    best = 0
    for i in range(len(tiles)):
        a = tiles[i]
        for j in range(i + 1, len(tiles)):
            b = tiles[j]
            x_lo, x_hi = sorted((a.x, b.x))
            y_lo, y_hi = sorted((a.y, b.y))
            area = (x_hi - x_lo + 1) * (y_hi - y_lo + 1)
            if area <= best:
                continue
            if all(
                (x, y) in filled
                for y in range(y_lo, y_hi + 1)
                for x in range(x_lo, x_hi + 1)
            ):
                best = area
    return best


def pick_volume(tiles: list[Tile]) -> int:
    """Return the number of red/green cells using Pick's theorem.

    With ``B`` boundary cells and shoelace area ``A`` (an integer for a lattice
    polygon), Pick's theorem gives interior lattice points
    ``I = A - B/2 + 1``, so the filled cell count is ``I + B = A + B/2 + 1``.
    This needs no scanline and no per-cell interior enumeration, so it works on
    the real input where the bounding box is far too large to flood-fill.
    """
    boundary = boundary_cells(tiles)
    if len(boundary) % 2 != 0:  # a closed loop has an even boundary-cell count
        raise ValueError("loop boundary has an odd number of cells")
    doubled = 0
    for i in range(len(tiles)):
        a = tiles[i]
        b = tiles[(i + 1) % len(tiles)]
        doubled += a.x * b.y - b.x * a.y
    area = abs(doubled) // 2
    return area + len(boundary) // 2 + 1


def _bank(name: str, coords: list[tuple[int, int]], expected: int) -> None:
    tiles = [Tile(x, y) for x, y in coords]
    reference = largest_rect(tiles)
    impl = day09.part2(tiles)
    assert reference == impl == expected, (name, reference, impl, expected)
    print(f"{name}: per-cell={reference} impl={impl}")


def _corpus() -> None:
    shapes = {
        "comb-u": [(0, 0), (5, 0), (5, 1), (1, 1), (1, 3), (5, 3), (5, 4), (0, 4)],
        "l-shape": [(0, 0), (4, 0), (4, 1), (1, 1), (1, 3), (0, 3)],
        "staircase": [(0, 0), (3, 0), (3, 2), (2, 2), (2, 1), (1, 1), (1, 3), (0, 3)],
        "t-shape": [
            (0, 0),
            (4, 0),
            (4, 1),
            (3, 1),
            (3, 3),
            (2, 3),
            (2, 1),
            (1, 1),
            (1, 3),
            (0, 3),
        ],
        "plus": [
            (0, 1),
            (1, 1),
            (1, 0),
            (2, 0),
            (2, 1),
            (4, 1),
            (4, 2),
            (2, 2),
            (2, 3),
            (1, 3),
            (1, 2),
            (0, 2),
        ],
        "two-notches": [
            (0, 0),
            (6, 0),
            (6, 2),
            (4, 2),
            (4, 1),
            (1, 1),
            (1, 2),
            (3, 2),
            (3, 4),
            (2, 4),
            (2, 5),
            (0, 5),
        ],
        "deep-u": [(0, 0), (2, 0), (2, 5), (1, 5), (1, 1), (0, 1)],
        "stair-notch": [
            (0, 0),
            (4, 0),
            (4, 2),
            (2, 2),
            (2, 3),
            (5, 3),
            (5, 4),
            (0, 4),
        ],
        "zigzag": [(0, 0), (3, 0), (3, 1), (1, 1), (1, 2), (2, 2), (2, 3), (0, 3)],
        "skinny-long": [(0, 0), (1, 0), (1, 6), (0, 6)],
        "square": [(0, 0), (4, 0), (4, 4), (0, 4)],
    }
    for name, coords in shapes.items():
        tiles = [Tile(x, y) for x, y in coords]
        reference = largest_rect(tiles)
        impl = day09.part2(tiles)
        assert reference == impl, (name, reference, impl)
    print(f"corpus: {len(shapes)} orthogonal-loop shapes verified")


def main() -> None:
    sample = day09.read_tiles(REPO_ROOT / "inputs" / "Day09Test.txt")
    real = day09.read_tiles(REPO_ROOT / "inputs" / "Day09.txt")

    sample_ref = largest_rect(sample)
    sample_impl = day09.part2(sample)
    assert sample_ref == sample_impl == 24, (sample_ref, sample_impl)
    print(f"sample: per-cell={sample_ref} impl={sample_impl}")

    _bank("tiny-square-loop", [(0, 0), (2, 0), (2, 2), (0, 2)], 9)
    _bank("thin-rectangle-loop", [(0, 0), (4, 0), (4, 1), (0, 1)], 10)
    _bank(
        "interior-notch",
        [(0, 0), (3, 0), (3, 1), (1, 1), (1, 3), (0, 3)],
        8,
    )
    _corpus()

    real_ref_volume = pick_volume(real)
    regions = day09._filled_regions(real)
    real_impl_volume = sum(
        (hi - lo + 1) * sum(b - a + 1 for a, b in intervals)
        for lo, hi, intervals in regions
    )
    assert real_ref_volume == real_impl_volume, (
        real_ref_volume,
        real_impl_volume,
    )
    print(f"real filled volume: pick={real_ref_volume} impl={real_impl_volume}")

    real_impl = day09.part2(real)
    assert real_impl == 1439894345, real_impl
    print(
        "real rectangle total 1439894345 reproduced by the implementation "
        "(per-cell reference is intractable on the ~9.3e9-cell bounding box)"
    )

    for name, tiles in {
        "empty": [],
        "one-tile": [Tile(0, 0)],
    }.items():
        for candidate in (largest_rect, day09.part2):
            try:
                candidate(tiles)
            except ValueError:
                pass
            else:  # pragma: no cover - a missing guard fails the check
                raise AssertionError(f"{name} did not raise ValueError")

    print("per-cell fill == implementation on sample, banks, and corpus")
    print("pick volume == implementation region volume on the real input")


if __name__ == "__main__":
    main()
