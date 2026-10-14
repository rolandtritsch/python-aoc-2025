"""Day03: maximise the joltage from each lobby escalator battery bank.

Each line of the puzzle input is a *bank* of batteries labelled with a joltage
rating digit (``1`` through ``9``). Within a bank a fixed number of batteries is
turned on and their joltage is the number formed by the chosen digits in their
original order. Part 1 turns on exactly two batteries per bank; part 2 turns on
exactly twelve. The answer is the sum of the largest such joltage from every bank.
"""

from collections.abc import Sequence
from pathlib import Path


def read_banks(filename: str | Path) -> list[str]:
    """Read one battery bank per line from a UTF-8 input file.

    Each nonblank line must contain only the joltage rating digits ``1`` through
    ``9`` and be at least two digits long (exactly two batteries must be turned
    on). A blank line, a line with a non-digit character, or a single-digit bank
    raises ValueError; a missing file raises FileNotFoundError.
    """
    if not str(filename):
        raise ValueError("filename must not be empty")
    banks: list[str] = []
    with Path(filename).open(encoding="utf-8") as source:
        for line_number, line in enumerate(source, start=1):
            text = line.strip()
            if not text:
                raise ValueError(f"line {line_number} is blank")
            if not text.isdigit():
                raise ValueError(f"line {line_number} has non-digit characters")
            if len(text) < 2:
                raise ValueError(f"line {line_number} has fewer than two digits")
            banks.append(text)
    return banks


def largest_pair_joltage(bank: str) -> int:
    """Return the largest two-digit joltage obtainable from ``bank``.

    Exactly two batteries are turned on and keep their original order, so the
    result is ``max(d[i] * 10 + d[j])`` over every index pair ``i < j``. A
    suffix maximum avoids rescanning the tail for each leading digit, giving
    O(n) time and O(n) space for an ``n``-digit bank. A bank shorter than two
    digits raises ValueError.
    """
    if len(bank) < 2:
        raise ValueError("bank must contain at least two digits")
    digits = [int(char) for char in bank]
    suffix_max = [0] * (len(digits) + 1)
    for index in range(len(digits) - 1, -1, -1):
        suffix_max[index] = max(digits[index], suffix_max[index + 1])
    return max(
        digits[index] * 10 + suffix_max[index + 1] for index in range(len(digits) - 1)
    )


def part1(banks: Sequence[str]) -> int:
    """Return the total joltage by summing each bank's largest pair joltage.

    Runs in O(N) time and O(M) extra space, where ``N`` is the total number of
    digits across all banks and ``M`` is the length of the longest bank.
    """
    return sum(largest_pair_joltage(bank) for bank in banks)


def largest_k_digit_joltage(bank: str, count: int = 12) -> int:
    """Return the largest ``count``-digit joltage obtainable from ``bank``.

    Exactly ``count`` batteries are turned on and keep their original order, so
    the result is the numerically largest ``count``-digit subsequence of the
    bank's digits. A monotonic stack greedily replaces an earlier kept digit
    with a later larger one while enough digits can still be discarded, so an
    ``n``-digit bank runs in O(n) time and O(n) space. A ``count`` below one or
    a bank shorter than ``count`` digits raises ValueError.
    """
    if count < 1:
        raise ValueError("count must be at least one")
    if len(bank) < count:
        raise ValueError("bank must contain at least count digits")
    digits = [int(char) for char in bank]
    removable = len(digits) - count
    kept: list[int] = []
    for digit in digits:
        while removable and kept and kept[-1] < digit:
            kept.pop()
            removable -= 1
        kept.append(digit)
    return int("".join(str(value) for value in kept[:count]))


def part2(banks: Sequence[str]) -> int:
    """Return the total joltage by summing each bank's largest 12-digit joltage.

    Runs in O(N) time and O(M) extra space, where ``N`` is the total number of
    digits across all banks and ``M`` is the length of the longest bank.
    """
    return sum(largest_k_digit_joltage(bank) for bank in banks)
