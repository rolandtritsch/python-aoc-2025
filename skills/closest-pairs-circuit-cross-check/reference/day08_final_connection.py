#!/usr/bin/env python3
"""Independent final-connection reference for AoC 2025 Day08 part2.

Continuing the Day08 part 1 connection process, the Elves keep connecting the
closest pairs of junction boxes (by straight-line distance) until every box is
in one circuit. Part 2 asks for the product of the X coordinates of the two
boxes whose connection first formed that single circuit. The official sample
finishes when boxes ``216,146,977`` and ``117,168,530`` connect, giving
``216 * 117 = 25272``; the real input finishes with boxes 661
``(80198,9816,87378)`` and 937 ``(75856,51,95679)``, giving ``6083499488``.

``src/aoc2025/day08.py`` ``_final_connection`` materializes every pair into a
min-heap keyed by ``(squared_distance, i, j)`` and pops until one component
remains, using a path-halving disjoint-set forest.

This reference is structurally independent of that implementation:

- It sorts a plain list of ``(distance, i, j)`` tuples instead of using a heap.
- It tracks circuits as a mapping of a representative box to a mutable ``set``
  of members and merges the smaller set into the larger, never using a parent
  array or path compression.

It is a self-checking demonstration for the ``closest-pairs-circuit-cross-check``
skill: it prints each total and asserts the reference equals the implementation
on the official sample, the real input, and boundary banks, and reports whether
the final-merge distance is unique (so the answer is tie-invariant). It is
read-only against the repository and needs no third-party packages.
"""

from __future__ import annotations

from pathlib import Path

from aoc2025 import day08
from aoc2025.day08 import Box

REPO_ROOT = Path(__file__).resolve().parents[3]


def _distance(a: Box, b: Box) -> int:
    """Return the squared straight-line distance between two boxes."""
    return (a.x - b.x) ** 2 + (a.y - b.y) ** 2 + (a.z - b.z) ** 2


def final_pair(boxes: list[Box]) -> tuple[int, int]:
    """Return the indices of the pair whose connection first joins one circuit.

    Pairs are materialized and sorted explicitly. A ``representative -> set``
    mapping holds circuit membership; merging folds the smaller set into the
    larger. Each pair whose boxes are in different circuits reduces the number
    of circuits by one, and the pair that reduces it to one is the final
    connection. The reference never mirrors the implementation's parent-array
    union-find, but it must use the same ``(distance, i, j)`` ordering so a
    distance tie resolves identically.
    """
    if len(boxes) < 2:
        raise ValueError("at least two boxes are required")
    pairs = sorted(
        (_distance(boxes[i], boxes[j]), i, j)
        for i in range(len(boxes))
        for j in range(i + 1, len(boxes))
    )
    representative = list(range(len(boxes)))
    members: dict[int, set[int]] = {i: {i} for i in range(len(boxes))}
    circuits = len(boxes)
    for _, i, j in pairs:
        left, right = representative[i], representative[j]
        if left == right:
            continue
        if len(members[left]) < len(members[right]):
            left, right = right, left
        for box_index in members[right]:
            representative[box_index] = left
        members[left] |= members[right]
        del members[right]
        circuits -= 1
        if circuits == 1:
            return i, j
    raise ValueError("boxes cannot form a single circuit")


def part2(boxes: list[Box]) -> int:
    """Return the product of the X coordinates of the final pair connected."""
    i, j = final_pair(boxes)
    return boxes[i].x * boxes[j].x


def final_merge_is_tie_free(boxes: list[Box]) -> bool:
    """Return True when the final-merge pair's distance is unique in the pair list.

    A tie at the final-merge distance would make "the pair that first completes
    one circuit" ambiguous and the product potentially order-dependent, so a
    real-input answer should be reported together with this check.
    """
    _, i, j = sorted(
        (_distance(boxes[i], boxes[j]), i, j)
        for i in range(len(boxes))
        for j in range(i + 1, len(boxes))
    )[0]
    distance = _distance(boxes[i], boxes[j])
    return (
        sum(
            _distance(boxes[a], boxes[b]) == distance
            for a in range(len(boxes))
            for b in range(a + 1, len(boxes))
        )
        == 1
    )


def main() -> None:
    sample = day08.read_boxes(REPO_ROOT / "inputs" / "Day08Test.txt")
    real = day08.read_boxes(REPO_ROOT / "inputs" / "Day08.txt")

    sample_ref = part2(sample)
    sample_impl = day08.part2(sample)
    assert sample_ref == sample_impl == 25272, (sample_ref, sample_impl)
    print(f"sample: merged-set={sample_ref} impl={sample_impl}")

    real_ref = part2(real)
    real_impl = day08.part2(real)
    assert real_ref == real_impl == 6083499488, (real_ref, real_impl)
    print(f"real:   merged-set={real_ref} impl={real_impl}")

    assert final_merge_is_tie_free(real), "real final-merge distance is not unique"
    print("real final-merge pair distance is unique (answer tie-invariant)")

    boundaries = {
        "two-boxes-single-pair": ([Box(3, 7, 9), Box(5, 1, 2)], 15),
        "three-line-finalises-outer": (
            [Box(0, 0, 0), Box(1, 0, 0), Box(2, 0, 0)],
            2,
        ),
        "two-clusters-closest-cross": (
            [Box(0, 0, 0), Box(1, 0, 0), Box(100, 0, 0), Box(101, 0, 0)],
            100,
        ),
        "final-not-max-x": (
            [Box(1, 0, 0), Box(100, 0, 0), Box(101, 0, 0), Box(1000, 0, 0)],
            101000,
        ),
        "ties-at-final-merge": (
            [Box(0, 0, 0), Box(1, 0, 0), Box(2, 0, 0), Box(3, 0, 0)],
            6,
        ),
        "uses-x-not-index": (
            [Box(2, 100, 0), Box(3, 200, 0), Box(1, 50, 0)],
            6,
        ),
    }
    for name, (boxes, expected) in boundaries.items():
        reference = part2(boxes)
        impl = day08.part2(boxes)
        assert reference == impl == expected, (name, reference, impl, expected)

    assert not final_merge_is_tie_free(
        [Box(0, 0, 0), Box(1, 0, 0), Box(2, 0, 0), Box(3, 0, 0)]
    ), "ties-at-final-merge should report a tied final-merge distance"

    for name, boxes in {
        "empty": [],
        "one-box": [Box(0, 0, 0)],
    }.items():
        for candidate in (part2, day08.part2):
            try:
                candidate(boxes)
            except ValueError:
                pass
            else:  # pragma: no cover - a missing guard fails the check
                raise AssertionError(f"{name} did not raise ValueError")

    print(f"boundaries: {len(boundaries)} banks verified, too-few-boxes raises")
    print("merged-set == implementation on all checks")


if __name__ == "__main__":
    main()
