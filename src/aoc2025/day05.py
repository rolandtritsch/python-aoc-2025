"""Day05: count how many available ingredient IDs are fresh.

The Cafeteria database lists inclusive fresh ingredient ID ranges (one
``first-last`` pair per line), a blank line, and then the available ingredient
IDs (one per line). An ID is fresh when it falls into at least one range, and
the ranges may overlap. Part 1 counts how many of the available IDs are fresh.
"""

import bisect
from collections.abc import Sequence
from pathlib import Path
from typing import NamedTuple


class IdRange(NamedTuple):
    """An inclusive fresh ingredient ID range from ``first`` through ``last``."""

    first: int
    last: int


class Database(NamedTuple):
    """A Cafeteria database: the fresh ID ranges and the available IDs."""

    ranges: list[IdRange]
    available: list[int]


def read_database(filename: str | Path) -> Database:
    """Read a Cafeteria database file into its ranges and available IDs.

    Every line before the first blank line is an inclusive ``first-last`` range
    with nonnegative integer bounds and ``first <= last``; every nonblank line
    after it is a nonnegative available ingredient ID. A malformed range, a
    reversed range, a malformed available ID, or a missing blank-line separator
    raises ValueError; a missing file raises FileNotFoundError.
    """
    if not str(filename):
        raise ValueError("filename must not be empty")
    ranges: list[IdRange] = []
    available: list[int] = []
    separator_seen = False
    with Path(filename).open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            text = line.strip()
            if not text:
                separator_seen = True
                continue
            if not separator_seen:
                bounds = text.split("-")
                if (
                    len(bounds) != 2
                    or not bounds[0].isdigit()
                    or not bounds[1].isdigit()
                ):
                    raise ValueError(f"line {line_number} has invalid range {text!r}")
                first, last = int(bounds[0]), int(bounds[1])
                if first > last:
                    raise ValueError(f"line {line_number} has reversed range {text!r}")
                ranges.append(IdRange(first, last))
            else:
                if not text.isdigit():
                    raise ValueError(f"line {line_number} has invalid ID {text!r}")
                available.append(int(text))
    if not separator_seen:
        raise ValueError("database must contain a blank-line separator")
    return Database(ranges, available)


def _merge_ranges(ranges: Sequence[IdRange]) -> list[IdRange]:
    """Return ``ranges`` sorted by ``first`` with overlaps and adjacencies merged.

    Two ranges whose ID intervals overlap or touch (the second ``first`` is at
    most one past the first ``last``) are combined into a single range, so a
    membership test needs only one interval per merged group. Runs in
    O(n log n) time for ``n`` ranges.
    """
    if not ranges:
        return []
    ordered = sorted(ranges)
    merged = [ordered[0]]
    for current in ordered[1:]:
        previous = merged[-1]
        if current.first <= previous.last + 1:
            if current.last > previous.last:
                merged[-1] = IdRange(previous.first, current.last)
        else:
            merged.append(current)
    return merged


def part1(ranges: Sequence[IdRange], available: Sequence[int]) -> int:
    """Return how many available ingredient IDs are fresh.

    An ID is fresh when it falls into at least one of the inclusive ranges.
    Overlapping ranges are merged and each available ID is tested against the
    merged intervals with a binary search. Runs in O(n log n + m log n) time
    and O(n) space for ``n`` ranges and ``m`` available IDs.
    """
    merged = _merge_ranges(ranges)
    if not merged:
        return 0
    starts = [interval.first for interval in merged]
    fresh = 0
    for identifier in available:
        index = bisect.bisect_right(starts, identifier) - 1
        if index >= 0 and identifier <= merged[index].last:
            fresh += 1
    return fresh
