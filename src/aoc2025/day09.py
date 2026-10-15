"""Day09: find the largest rectangle whose opposite corners are red tiles.

Red tiles sit at integer ``(x, y)`` positions on a large grid. Any two red
tiles can be chosen as the opposite corners of an axis-aligned rectangle; the
rectangle's area counts every grid cell it spans, including both corner tiles.
Part 1 returns the largest such area over every pair of red tiles. Part 2
first fills in the green tiles (the loop connecting consecutive red tiles plus
its interior) and then returns the largest red-cornered rectangle made entirely
of red and green tiles.
"""

from bisect import bisect_right
from collections.abc import Sequence
from pathlib import Path
from typing import NamedTuple


class Tile(NamedTuple):
    """A red tile at integer coordinates ``x`` and ``y``."""

    x: int
    y: int


def read_tiles(filename: str | Path) -> list[Tile]:
    """Read one ``x,y`` coordinate pair per line into a list of tiles.

    Each nonblank line must hold two non-negative integers separated by a
    comma. A blank line, a malformed pair, a missing comma, or a non-integer
    coordinate raises ValueError; a missing file raises FileNotFoundError.
    """
    if not str(filename):
        raise ValueError("filename must not be empty")
    tiles: list[Tile] = []
    with Path(filename).open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            text = line.strip()
            if not text:
                raise ValueError(f"line {line_number} is blank")
            parts = text.split(",")
            if len(parts) != 2 or not all(part.strip().isdigit() for part in parts):
                raise ValueError(f"line {line_number} has invalid coordinate {text!r}")
            tiles.append(Tile(*(int(part) for part in parts)))
    return tiles


def _rectangle_area(a: Tile, b: Tile) -> int:
    """Return the area of the axis-aligned rectangle with corners ``a`` and ``b``.

    The rectangle spans every grid cell between the two tiles inclusive, so its
    width is ``|a.x - b.x| + 1`` and its height is ``|a.y - b.y| + 1``.
    """
    width = abs(a.x - b.x) + 1
    height = abs(a.y - b.y) + 1
    return width * height


def part1(tiles: Sequence[Tile]) -> int:
    """Return the largest area of a rectangle with two red-tile corners.

    Every pair of red tiles defines an axis-aligned rectangle with those two
    tiles at opposite corners, and its area counts both corner tiles. Rejects
    fewer than two tiles. Runs in O(N^2) time and O(1) extra space for ``N``
    tiles.
    """
    if len(tiles) < 2:
        raise ValueError("at least two tiles are required")
    return max(
        _rectangle_area(tiles[i], tiles[j])
        for i in range(len(tiles))
        for j in range(i + 1, len(tiles))
    )


def _edges(
    tiles: Sequence[Tile],
) -> tuple[list[tuple[int, int, int]], list[tuple[int, int, int]]]:
    """Return the loop's vertical and horizontal edge segments.

    Consecutive tiles (with the list wrapping so the last tile connects back to
    the first) are joined by a straight segment on a shared row or column. Each
    vertical edge is ``(x, y_lo, y_hi)`` and each horizontal edge is
    ``(y, x_lo, x_hi)`` with the range sorted ascending.
    """
    vertical: list[tuple[int, int, int]] = []
    horizontal: list[tuple[int, int, int]] = []
    for i in range(len(tiles)):
        a = tiles[i]
        b = tiles[(i + 1) % len(tiles)]
        if a.x == b.x:
            lo, hi = sorted((a.y, b.y))
            vertical.append((a.x, lo, hi))
        else:
            lo, hi = sorted((a.x, b.x))
            horizontal.append((a.y, lo, hi))
    return vertical, horizontal


def _cover_at(y: int, vertical, horizontal) -> tuple[tuple[int, int], ...]:
    """Return the merged red/green ``(x_lo, x_hi)`` intervals covering row ``y``.

    Vertical edges are treated as half-open ``[y_lo, y_hi)`` walls so the
    even-odd rule pairs their columns into filled interior strips; any
    horizontal edge coincident with the row is added back as a boundary strip
    so fully filled rows and their edges are included.
    """
    crosses = sorted({x for x, y_lo, y_hi in vertical if y_lo <= y < y_hi})
    intervals = [(crosses[k], crosses[k + 1]) for k in range(0, len(crosses) - 1, 2)]
    intervals.extend((x_lo, x_hi) for y_row, x_lo, x_hi in horizontal if y_row == y)
    intervals.sort()
    merged: list[tuple[int, int]] = []
    for lo, hi in intervals:
        if merged and lo <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], hi))
        else:
            merged.append((lo, hi))
    return tuple(merged)


def _filled_regions(
    tiles: Sequence[Tile],
) -> list[tuple[int, int, tuple[tuple[int, int], ...]]]:
    """Return the red/green region as ``(y_lo, y_hi, intervals)`` rows.

    The filled x-intervals are identical for every row strictly inside a gap
    between two consecutive tile y-coordinates, and possibly different on the
    exact tile rows where horizontal edges lie. Consecutive regions that share
    an identical interval set are merged so the result is a compact, ordered
    list keyed by y-range.
    """
    vertical, horizontal = _edges(tiles)
    y_coords = sorted({t.y for t in tiles})
    regions: list[tuple[int, int, tuple[tuple[int, int], ...]]] = []
    for y in y_coords:
        regions.append((y, y, _cover_at(y, vertical, horizontal)))
    for y_lo, y_hi in zip(y_coords, y_coords[1:], strict=False):
        if y_lo + 1 <= y_hi - 1:
            regions.append(
                (y_lo + 1, y_hi - 1, _cover_at(y_lo + 1, vertical, horizontal))
            )
    regions.sort(key=lambda region: region[0])
    merged_regions: list[tuple[int, int, tuple[tuple[int, int], ...]]] = []
    for y_lo, y_hi, intervals in regions:
        if (
            merged_regions
            and merged_regions[-1][2] == intervals
            and merged_regions[-1][1] + 1 == y_lo
        ):
            merged_regions[-1] = (merged_regions[-1][0], y_hi, merged_regions[-1][2])
        else:
            merged_regions.append((y_lo, y_hi, intervals))
    return merged_regions


def _covers(intervals: tuple[tuple[int, int], ...], x_lo: int, x_hi: int) -> bool:
    """Return whether ``[x_lo, x_hi]`` is fully inside the interval union."""
    starts = [lo for lo, _ in intervals]
    index = bisect_right(starts, x_lo) - 1
    if index < 0:
        return False
    return intervals[index][1] >= x_hi


def part2(tiles: Sequence[Tile]) -> int:
    """Return the largest red/green-only rectangle with two red-tile corners.

    The red tiles form a simple closed orthogonal loop: consecutive tiles share
    a row or column, and the list wraps. Its boundary and interior are the
    "red or green" tiles. We build that filled region as per-row x-intervals
    and evaluate every pair of red tiles as opposite corners, keeping the
    largest area whose entire rectangle is covered. Rejects fewer than two
    tiles. Runs in O(N^2 log N) time for ``N`` tiles in the common case.
    """
    if len(tiles) < 2:
        raise ValueError("at least two tiles are required")
    regions = _filled_regions(tiles)
    cache: dict[tuple[tuple[tuple[int, int], ...], int, int], bool] = {}
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
            valid = True
            for region_lo, region_hi, intervals in regions:
                if region_hi < y_lo:
                    continue
                if region_lo > y_hi:
                    break
                key = (intervals, x_lo, x_hi)
                covered = cache.get(key)
                if covered is None:
                    covered = _covers(intervals, x_lo, x_hi)
                    cache[key] = covered
                if not covered:
                    valid = False
                    break
            if valid:
                best = area
    return best
