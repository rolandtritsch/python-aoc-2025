#!/usr/bin/env python3
"""Independent closest-pairs circuit reference for AoC 2025 Day08 part1.

The Elves connect the ``connections`` closest pairs of junction boxes (by
straight-line distance), skipping any pair whose two boxes are already in the
same circuit, then multiply the sizes of the three largest circuits. The
subtlety is that *examined* pairs consume the connection budget even when they
are skipped: the sample examines 10 closest pairs, one of which is already
in-circuit, and the stated answer is 40. A reading where skips do not consume a
slot would give 50, so "examine the K closest pairs" is the confirmed rule.

``src/aoc2025/day08.py`` ``_circuit_sizes`` materializes every pair into a
min-heap keyed by ``(squared_distance, i, j)``, pops the K closest pairs, and
unions different roots with a path-halving disjoint-set forest.

This reference is structurally independent of that implementation:

- It sorts a plain list of ``(distance, i, j)`` tuples instead of using a heap.
- It tracks circuits as a mapping of a representative box to a mutable ``set``
  of members and merges the smaller set into the larger, never using a parent
  array or path compression.

It is a self-checking demonstration for the ``closest-pairs-circuit-cross-check``
skill: it prints each total and asserts the reference equals the implementation
on the official sample, the real input, the boundary banks, and a skip-slot
distinction. It is read-only against the repository and needs no third-party
packages.
"""

from __future__ import annotations

from pathlib import Path

from aoc2025 import day08
from aoc2025.day08 import Box

REPO_ROOT = Path(__file__).resolve().parents[3]


def _distance(a: Box, b: Box) -> int:
    """Return the squared straight-line distance between two boxes."""
    return (a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2


def circuit_sizes(boxes: list[Box], connections: int) -> list[int]:
    """Return sorted circuit sizes after examining the ``connections`` closest pairs.

    Pairs are materialized and sorted explicitly. A ``representative -> set``
    mapping holds circuit membership; an examined pair whose boxes already share
    a representative is skipped but still consumes one of the ``connections``
    examined pairs, matching the sample. Merging always folds the smaller set
    into the larger, so the reference never mirrors the implementation's
    parent-array union-find.
    """
    n = len(boxes)
    pairs = sorted(
        (_distance(boxes[i], boxes[j]), i, j) for i in range(n) for j in range(i + 1, n)
    )
    representative = list(range(n))
    members: dict[int, set[int]] = {i: {i} for i in range(n)}
    for _, i, j in pairs[:connections]:
        left, right = representative[i], representative[j]
        if left == right:
            continue
        if len(members[left]) < len(members[right]):
            left, right = right, left
        for box_index in members[right]:
            representative[box_index] = left
        members[left] |= members[right]
        del members[right]
    return sorted(len(group) for group in members.values())


def part1(boxes: list[Box], connections: int = 1000) -> int:
    """Return the product of the three largest circuit sizes."""
    if len(boxes) < 3:
        raise ValueError("at least three boxes are required")
    sizes = circuit_sizes(boxes, connections)
    result = 1
    for circuit in sizes[-3:]:
        result *= circuit
    return result


def cutoff_is_tie_free(boxes: list[Box], connections: int) -> bool:
    """Return True when the K-th closest distance is unique in the pair list.

    A tie spanning the cutoff would make "the K closest pairs" ambiguous and the
    product potentially order-dependent, so a real-input answer should be
    reported together with this check.
    """
    distances = sorted(
        _distance(boxes[i], boxes[j])
        for i in range(len(boxes))
        for j in range(i + 1, len(boxes))
    )
    cutoff = distances[connections - 1]
    return distances.count(cutoff) == 1


def main() -> None:
    sample = day08.read_boxes(REPO_ROOT / "inputs" / "Day08Test.txt")
    real = day08.read_boxes(REPO_ROOT / "inputs" / "Day08.txt")

    sample_ref = part1(sample, connections=10)
    sample_impl = day08.part1(sample, connections=10)
    assert sample_ref == sample_impl == 40, (sample_ref, sample_impl)
    print(f"sample: sorted-set={sample_ref} impl={sample_impl}")

    real_ref = part1(real, connections=1000)
    real_impl = day08.part1(real)
    assert real_ref == real_impl == 90036, (real_ref, real_impl)
    print(f"real:   sorted-set={real_ref} impl={real_impl}")

    assert cutoff_is_tie_free(real, 1000), "real cutoff distance is not unique"
    print("real 1000-pair cutoff distance is unique (answer tie-invariant)")

    boundaries = {
        "three-line": ([Box(0, 0, 0), Box(1, 0, 0), Box(2, 0, 0)], 2),
        "three-line-connect-one": ([Box(0, 0, 0), Box(1, 0, 0), Box(2, 0, 0)], 1),
        "four-two-pairs": (
            [Box(0, 0, 0), Box(1, 0, 0), Box(100, 0, 0), Box(101, 0, 0)],
            2,
        ),
        "five-two-pairs-singleton": (
            [
                Box(0, 0, 0),
                Box(1, 0, 0),
                Box(100, 0, 0),
                Box(101, 0, 0),
                Box(1000, 0, 0),
            ],
            2,
        ),
        "skip-consumes-slot": (
            [Box(0, 0, 0), Box(1, 0, 0), Box(2, 0, 0), Box(4, 0, 0)],
            3,
        ),
        "ties-at-cutoff": (
            [Box(0, 0, 0), Box(0, 0, 1), Box(1, 0, 0), Box(1, 0, 1)],
            2,
        ),
        "connect-everything": (
            [Box(0, 0, 0), Box(1, 0, 0), Box(2, 0, 0), Box(3, 0, 0)],
            100,
        ),
        "disconnected-clusters": (
            [Box(0, 0, 0), Box(1, 0, 0), Box(1000, 0, 0), Box(1001, 0, 0)],
            2,
        ),
        "already-connected-skip": (
            [Box(0, 0, 0), Box(0, 0, 1), Box(0, 0, 2)],
            3,
        ),
    }
    for name, (boxes, connections) in boundaries.items():
        reference = part1(boxes, connections)
        impl = day08.part1(boxes, connections)
        assert reference == impl, (name, reference, impl)

    for name, boxes in {
        "empty": [],
        "one-box": [Box(0, 0, 0)],
        "two-boxes": [Box(0, 0, 0), Box(1, 1, 1)],
    }.items():
        for candidate in (part1, day08.part1):
            try:
                candidate(boxes)
            except ValueError:
                pass
            else:  # pragma: no cover - a missing guard fails the check
                raise AssertionError(f"{name} did not raise ValueError")

    print(f"boundaries: {len(boundaries)} banks verified, too-few-boxes raises")
    print("sorted-set == implementation on all checks")


if __name__ == "__main__":
    main()
