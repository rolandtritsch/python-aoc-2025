#!/usr/bin/env python3
"""Independent naive membership reference for AoC 2025 Day05 part1.

The Cafeteria database lists inclusive fresh ingredient ID ranges and then the
available ingredient IDs. Part 1 counts how many available IDs are fresh, i.e.
fall into at least one range. This reference counts by scanning every raw range
for each available ID — no merging, no binary search, no shared helper — so it
is structurally independent of the implementation under review
(``src/aoc2025/day05.py`` part1, which merges overlapping/adjacent ranges and
then binary-searches each ID).

This is a self-checking demonstration for the ``range-membership-cross-check``
skill: it prints each total and asserts naive == implementation throughout on
the official sample, the real input, and interval boundary banks. It is
read-only against the repository and needs no third-party packages.
"""

from __future__ import annotations

from pathlib import Path

from aoc2025 import day05
from aoc2025.day05 import IdRange

REPO_ROOT = Path(__file__).resolve().parents[3]


def naive_fresh_count(ranges: list[IdRange], available: list[int]) -> int:
    """Return how many available IDs fall into at least one inclusive range.

    Each ID is tested against every range directly, so the reference never
    reuses the implementation's merge-then-binary-search structure. Runs in
    O(n * m) time for n ranges and m available IDs, which is fine for the small
    fixtures used here.
    """
    return sum(
        any(first <= identifier <= last for first, last in ranges)
        for identifier in available
    )


def main() -> None:
    sample = day05.read_database(REPO_ROOT / "inputs" / "Day05Test.txt")
    sample_ref = naive_fresh_count(sample.ranges, sample.available)
    sample_impl = day05.part1(sample.ranges, sample.available)
    assert sample_ref == sample_impl == 3, (sample_ref, sample_impl)

    real = day05.read_database(REPO_ROOT / "inputs" / "Day05.txt")
    real_ref = naive_fresh_count(real.ranges, real.available)
    real_impl = day05.part1(real.ranges, real.available)
    assert real_ref == real_impl == 848, (real_ref, real_impl)

    boundaries = {
        "empty": ([], []),
        "no-ranges": ([], [1, 5, 8]),
        "no-available": ([IdRange(1, 10)], []),
        "inclusive-bounds": ([IdRange(3, 5)], [3, 4, 5]),
        "just-outside": ([IdRange(3, 5)], [2, 6]),
        "below-every-range": ([IdRange(10, 20), IdRange(30, 40)], [5]),
        "above-every-range": ([IdRange(10, 20), IdRange(30, 40)], [50]),
        "in-gap": ([IdRange(10, 20), IdRange(30, 40)], [25]),
        "overlap-once": ([IdRange(16, 20), IdRange(12, 18)], [17, 17, 1]),
        "adjacent-touching": ([IdRange(1, 3), IdRange(4, 6)], [3, 4, 7]),
        "contained": ([IdRange(10, 20), IdRange(12, 15)], [12, 15, 9, 21]),
        "single-point": ([IdRange(5, 5)], [5, 4, 6]),
        "duplicate-available": ([IdRange(3, 5)], [3, 3, 5]),
    }
    for name, (ranges, available) in boundaries.items():
        reference = naive_fresh_count(ranges, available)
        impl = day05.part1(ranges, available)
        assert reference == impl, (name, reference, impl)

    print(f"sample: naive={sample_ref} impl={sample_impl}")
    print(f"real:   naive={real_ref} impl={real_impl}")
    print(f"boundaries: {len(boundaries)} interval banks verified")
    print("naive == implementation on all checks")


if __name__ == "__main__":
    main()
