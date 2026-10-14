"""Day09: find the largest rectangle whose opposite corners are red tiles.

Red tiles sit at integer ``(x, y)`` positions on a large grid. Any two red
tiles can be chosen as the opposite corners of an axis-aligned rectangle; the
rectangle's area counts every grid cell it spans, including both corner tiles.
Part 1 returns the largest such area over every pair of red tiles.
"""

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
