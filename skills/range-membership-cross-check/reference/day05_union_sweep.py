#!/usr/bin/env python3
"""Independent sweep-line union reference for AoC 2025 Day05 part2.

The fresh ingredient ID ranges are inclusive integer intervals that may
overlap; part 2 counts every distinct ID the ranges themselves mark as fresh,
i.e. the number of integer points covered by the union of the ranges
(``src/aoc2025/day05.py`` part2, which merges overlapping/adjacent ranges and
sums the merged intervals' lengths). This reference counts the same union
length with an endpoint sweep: a +1 event at each ``first``, a -1 event at
each ``last + 1``, then a walk over sorted coordinates that accumulates the
integer span whenever the active count is positive. It never merges ranges,
never sums merged lengths, and shares no helper with the implementation, so it
is structurally independent of ``_merge_ranges`` and ``part2``.

This is a self-checking demonstration for the ``range-membership-cross-check``
skill: it prints each total and asserts sweep == implementation throughout on
the official sample, the real input, and interval-union boundary banks. It is
read-only against the repository and needs no third-party packages.
"""

from __future__ import annotations

from pathlib import Path

from aoc2025 import day05
from aoc2025.day05 import IdRange

REPO_ROOT = Path(__file__).resolve().parents[3]


def union_length_sweep(ranges: list[IdRange]) -> int:
    """Return the number of integer coordinates covered by at least one range.

    An inclusive interval ``first..last`` contributes +1 coverage starting at
    ``first`` and -1 starting at ``last + 1``; walking the sorted event
    coordinates and summing any span where coverage is positive yields the
    union length without merging intervals. Runs in O(n log n) time and O(n)
    space for ``n`` ranges.
    """
    events: dict[int, int] = {}
    for first, last in ranges:
        events[first] = events.get(first, 0) + 1
        events[last + 1] = events.get(last + 1, 0) - 1
    total = 0
    active = 0
    previous: int | None = None
    for coordinate in sorted(events):
        if previous is not None and active > 0:
            total += coordinate - previous
        active += events[coordinate]
        previous = coordinate
    return total


def main() -> None:
    sample = day05.read_database(REPO_ROOT / "inputs" / "Day05Test.txt")
    sample_ref = union_length_sweep(sample.ranges)
    sample_impl = day05.part2(sample.ranges)
    assert sample_ref == sample_impl == 14, (sample_ref, sample_impl)

    real = day05.read_database(REPO_ROOT / "inputs" / "Day05.txt")
    real_ref = union_length_sweep(real.ranges)
    real_impl = day05.part2(real.ranges)
    assert real_ref == real_impl == 334714395325710, (real_ref, real_impl)

    boundaries = {
        "no-ranges": [],
        "single-point": [IdRange(7, 7)],
        "inclusive-endpoints": [IdRange(3, 5)],
        "disjoint-sum-lengths": [IdRange(1, 3), IdRange(10, 12)],
        "overlap-count-once": [IdRange(16, 20), IdRange(12, 18)],
        "adjacent-touching-merge": [IdRange(1, 3), IdRange(4, 6)],
        "contained-adds-nothing": [IdRange(10, 20), IdRange(12, 15)],
        "contained-touching-endpoint": [IdRange(10, 20), IdRange(20, 22)],
        "many-single-points": [IdRange(1, 1), IdRange(3, 3), IdRange(5, 5)],
        "unsorted-input": [IdRange(30, 40), IdRange(1, 5), IdRange(10, 12)],
    }
    for name, ranges in boundaries.items():
        reference = union_length_sweep(ranges)
        impl = day05.part2(ranges)
        assert reference == impl, (name, reference, impl)

    print(f"sample: sweep={sample_ref} impl={sample_impl}")
    print(f"real:   sweep={real_ref} impl={real_impl}")
    print(f"boundaries: {len(boundaries)} interval-union banks verified")
    print("sweep == implementation on all checks")


if __name__ == "__main__":
    main()
