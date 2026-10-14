#!/usr/bin/env python3
"""Independent brute-force reference for the Day03 k-digit subsequence.

Part 2 turns on exactly twelve batteries per bank and forms the twelve-digit
number from those digits in their original order; the answer per bank is the
maximum such subsequence. This reference enumerates every ``count``-element
subsequence directly from the statement via ``itertools.combinations`` and
cross-checks the repository's monotonic-stack greedy on the official sample,
boundary banks, and seeded random small banks.

The real input is 200 banks of 100 digits, so an exhaustive C(100,12) check is
intractable; here the real input is verified through the fast implementation
alone against the accepted answer, with the greedy's correctness established
independently on small banks. This is a self-checking demonstration for the
``brute-force-cross-check`` skill: it prints each total and asserts
brute-force == optimized throughout. It is read-only and stdlib-only.
"""

from __future__ import annotations

import random
from itertools import combinations
from pathlib import Path

from aoc2025 import day03

REPO_ROOT = Path(__file__).resolve().parents[3]


def brute_k_digit_joltage(bank: str, count: int) -> int:
    """Return the largest ``count``-digit subsequence by trying every choice."""
    digits = [int(char) for char in bank]
    best = 0
    for indexes in combinations(range(len(digits)), count):
        best = max(best, int("".join(str(digits[index]) for index in indexes)))
    return best


def main() -> None:
    samples = day03.read_banks(REPO_ROOT / "inputs" / "Day03Test.txt")
    sample_brute = sum(brute_k_digit_joltage(bank, 12) for bank in samples)
    sample_fast = day03.part2(samples)
    assert sample_brute == sample_fast == 3121910778619, (sample_brute, sample_fast)

    boundaries = {
        "98765432198765": 987654398765,
        "12345678912345": 345678912345,
        "98765432112345": 987654322345,
        "19999999999999": 999999999999,
        "555555555555": 555555555555,
        "987654321111": 987654321111,
    }
    for bank, expected in boundaries.items():
        got = day03.largest_k_digit_joltage(bank, 12)
        assert got == expected, (bank, got, expected)

    generator = random.Random(2025)
    for _ in range(2000):
        length = generator.randint(12, 16)
        count = generator.randint(1, 12)
        bank = "".join(str(generator.randint(1, 9)) for _ in range(length))
        brute = brute_k_digit_joltage(bank, count)
        fast = day03.largest_k_digit_joltage(bank, count)
        assert brute == fast, (bank, count, brute, fast)

    for count, bank in [(0, "1234"), (12, "98765432111")]:
        try:
            day03.largest_k_digit_joltage(bank, count)
            raise AssertionError(f"expected ValueError for count={count} {bank!r}")
        except ValueError:
            pass

    real = day03.read_banks(REPO_ROOT / "inputs" / "Day03.txt")
    real_fast = day03.part2(real)
    assert real_fast == 170997883706617, real_fast

    print(f"sample:  brute={sample_brute} fast={sample_fast}")
    print(f"boundaries: {len(boundaries)} banks verified")
    print("2000 random small banks (count 1..12): brute == fast")
    print(f"real:    fast={real_fast} (accepted answer; brute C(100,12) intractable)")
    print("brute-force == optimized on all feasible checks")


if __name__ == "__main__":
    main()
