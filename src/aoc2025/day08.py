"""Day08: connect closest junction boxes into circuits.

Junction boxes sit at 3D ``(x, y, z)`` positions. Connecting two boxes lets
electricity flow between them, placing them in the same circuit. The Elves walk
all pairs in order of increasing straight-line (Euclidean) distance and connect
a pair unless its two boxes are already in the same circuit. Part 1 stops after
a fixed number of closest pairs have been examined and multiplies the sizes of
the three largest circuits; part 2 keeps connecting until every box is in one
circuit and multiplies the X coordinates of the pair that completed it.
"""

from collections.abc import Sequence
from heapq import heappop, heappush
from pathlib import Path
from typing import NamedTuple


class Box(NamedTuple):
    """A junction box at 3D coordinates ``x``, ``y``, ``z``."""

    x: int
    y: int
    z: int


def read_boxes(filename: str | Path) -> list[Box]:
    """Read one ``x,y,z`` coordinate triple per line into a list of boxes.

    Each nonblank line must hold three integers separated by commas. A blank
    line, a malformed triple, a missing comma, or a non-integer coordinate
    raises ValueError; a missing file raises FileNotFoundError.
    """
    if not str(filename):
        raise ValueError("filename must not be empty")
    boxes: list[Box] = []
    with Path(filename).open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            text = line.strip()
            if not text:
                raise ValueError(f"line {line_number} is blank")
            parts = text.split(",")
            if len(parts) != 3 or not all(part.strip().isdigit() for part in parts):
                raise ValueError(f"line {line_number} has invalid triple {text!r}")
            boxes.append(Box(*(int(part) for part in parts)))
    return boxes


def _squared_distance(a: Box, b: Box) -> int:
    """Return the squared Euclidean distance between two boxes."""
    dx = a.x - b.x
    dy = a.y - b.y
    dz = a.z - b.z
    return dx * dx + dy * dy + dz * dz


def _circuit_sizes(boxes: Sequence[Box], connections: int) -> list[int]:
    """Return circuit sizes after examining the ``connections`` closest pairs.

    A disjoint-set forest connects the two boxes of each examined pair that are
    not yet in the same circuit. Pairs already inside one circuit are skipped
    without consuming an extra slot in ``connections``. Runs in
    O(N^2 log N) time and O(N) space for ``N`` boxes.
    """
    n = len(boxes)
    parent = list(range(n))
    size = [1] * n

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    heap: list[tuple[int, int, int]] = []
    for i in range(n):
        for j in range(i + 1, n):
            heappush(heap, (_squared_distance(boxes[i], boxes[j]), i, j))
    examined = 0
    while heap and examined < connections:
        _, i, j = heappop(heap)
        examined += 1
        root_i, root_j = find(i), find(j)
        if root_i != root_j:
            parent[root_i] = root_j
            size[root_j] += size[root_i]
    return sorted(size[i] for i in range(n) if find(i) == i)


def part1(boxes: Sequence[Box], connections: int = 1000) -> int:
    """Return the product of the three largest circuit sizes.

    Connect the ``connections`` closest pairs of boxes (skipping any pair whose
    boxes already share a circuit), then multiply the sizes of the three largest
    resulting circuits. Rejects fewer than three boxes.
    """
    if len(boxes) < 3:
        raise ValueError("at least three boxes are required")
    sizes = _circuit_sizes(boxes, connections)
    result = 1
    for circuit in sizes[-3:]:
        result *= circuit
    return result


def _final_connection(boxes: Sequence[Box]) -> tuple[int, int]:
    """Return the boxes whose connection first joins every box into one circuit.

    Pops all pairs in increasing squared distance (indexes break ties, matching
    the heap ordering of ``_circuit_sizes``) and unions each pair whose boxes are
    in different circuits until a single circuit remains. Returns the indices of
    the pair that produced that final merge. Runs in O(N^2 log N) time and
    O(N^2) space for ``N`` boxes, since every pair is materialized in the heap.
    """
    n = len(boxes)
    parent = list(range(n))
    size = [1] * n

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    heap: list[tuple[int, int, int]] = []
    for i in range(n):
        for j in range(i + 1, n):
            heappush(heap, (_squared_distance(boxes[i], boxes[j]), i, j))
    components = n
    while heap:
        _, i, j = heappop(heap)
        root_i, root_j = find(i), find(j)
        if root_i != root_j:
            parent[root_i] = root_j
            size[root_j] += size[root_i]
            components -= 1
            if components == 1:
                return i, j
    raise ValueError("boxes cannot form a single circuit")


def part2(boxes: Sequence[Box]) -> int:
    """Return the product of the X coordinates of the final pair connected.

    Connect the closest pairs of boxes until every box belongs to one circuit,
    then multiply the X coordinates of the two boxes whose connection first
    formed that single circuit. Rejects fewer than two boxes.
    """
    if len(boxes) < 2:
        raise ValueError("at least two boxes are required")
    i, j = _final_connection(boxes)
    return boxes[i].x * boxes[j].x
