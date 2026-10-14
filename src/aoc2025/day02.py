"""Day02: identify invalid gift shop product IDs across digit ranges.

The puzzle input is a single comma-separated line of inclusive ID ranges, each
written ``first-last``. Part 1 defines an invalid ID as one whose decimal form
is some nonempty digit sequence repeated exactly twice (``55``, ``6464``,
``123123``); Part 2 relaxes that to a sequence repeated at least twice
(``123123123``, ``1111111``). The answer is the sum of every invalid ID
appearing in any range.
"""

from collections.abc import Sequence
from pathlib import Path
from typing import NamedTuple


class IdRange(NamedTuple):
    """An inclusive product ID range from ``first`` through ``last``."""

    first: int
    last: int


def read_ranges(filename: str | Path) -> list[IdRange]:
    """Read comma-separated inclusive ID ranges from a UTF-8 input file.

    Each nonblank line is split on commas; every token is a ``first-last``
    pair of nonnegative integers with ``first <= last``. Blank lines are
    skipped. A missing file raises FileNotFoundError; an empty token, a
    malformed range, a non-numeric bound, or a reversed range raises
    ValueError.
    """
    if not str(filename):
        raise ValueError("filename must not be empty")
    ranges: list[IdRange] = []
    with Path(filename).open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            text = line.strip()
            if not text:
                continue
            for token in text.split(","):
                token = token.strip()
                bounds = token.split("-")
                if (
                    len(bounds) != 2
                    or not bounds[0].isdigit()
                    or not bounds[1].isdigit()
                ):
                    raise ValueError(f"line {line_number} has invalid range {token!r}")
                first, last = int(bounds[0]), int(bounds[1])
                if first > last:
                    raise ValueError(f"line {line_number} has reversed range {token!r}")
                ranges.append(IdRange(first, last))
    return ranges


def is_repeated_twice(number: int) -> bool:
    """Return whether ``number`` is a digit sequence repeated exactly twice.

    The decimal form must have even length and consist of two identical
    halves. Negative numbers raise ValueError. Runs in O(d) time for a
    number with ``d`` digits.
    """
    if number < 0:
        raise ValueError("number must be nonnegative")
    text = str(number)
    if len(text) % 2:
        return False
    half = len(text) // 2
    return text[:half] == text[half:]


def is_repeated_at_least_twice(number: int) -> bool:
    """Return whether ``number`` is a digit sequence repeated at least twice.

    The decimal form must equal some nonempty prefix repeated ``k`` times for
    an integer ``k >= 2``. This subsumes the exactly-twice case and also
    accepts ``123123123`` (``123`` three times) and ``1111111`` (``1`` seven
    times). Negative numbers raise ValueError. Runs in O(d^2) time for a
    number with ``d`` digits.
    """
    if number < 0:
        raise ValueError("number must be nonnegative")
    text = str(number)
    length = len(text)
    for divisor in range(1, length // 2 + 1):
        if length % divisor == 0 and text == text[:divisor] * (length // divisor):
            return True
    return False


def part1(ranges: Sequence[IdRange]) -> int:
    """Return the sum of all invalid IDs appearing across ``ranges``.

    Each range is scanned inclusively and every ID whose decimal form is a
    digit sequence repeated exactly twice is added to the total. Runs in
    O(T) time, where ``T`` is the total number of IDs across all ranges.
    """
    total = 0
    for first, last in ranges:
        for number in range(first, last + 1):
            if is_repeated_twice(number):
                total += number
    return total


def part2(ranges: Sequence[IdRange]) -> int:
    """Return the sum of all invalid IDs appearing across ``ranges``.

    Each range is scanned inclusively and every ID whose decimal form is a
    digit sequence repeated at least twice is added to the total. Runs in
    O(T * d) time, where ``T`` is the total number of IDs across all ranges
    and ``d`` is the maximum number of digits in any ID.
    """
    total = 0
    for first, last in ranges:
        for number in range(first, last + 1):
            if is_repeated_at_least_twice(number):
                total += number
    return total
