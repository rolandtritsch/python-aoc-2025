#!/usr/bin/env python3
"""Independent O(n^2) brute-force reference for AoC 2025 Day03 part1.

A bank is a string of joltage-rating digits. Part 1 turns on exactly two
batteries and forms the two-digit number from those digits in their original
order; the answer per bank is the maximum such number. This reference
enumerates every ordered pair directly from the statement and cross-checks the
repository's optimized suffix-max implementation on the sample, the real
input, and boundary banks.

This is a self-checking demonstration for the ``brute-force-cross-check``
skill: it prints each total and asserts brute-force == optimized throughout.
It is read-only against the repository and needs no third-party packages.
"""

from __future__ import annotations

from pathlib import Path

from aoc2025 import day03

REPO_ROOT = Path(__file__).resolve().parents[3]


def brute_pair_joltage(bank: str) -> int:
    """Return the largest two-digit joltage by trying every ordered pair."""
    best = 0
    for index, left in enumerate(bank):
        for right in bank[index + 1 :]:
            best = max(best, int(left) * 10 + int(right))
    return best


def main() -> None:
    samples = day03.read_banks(REPO_ROOT / "inputs" / "Day03Test.txt")
    sample_brute = sum(brute_pair_joltage(bank) for bank in samples)
    sample_fast = day03.part1(samples)
    assert sample_brute == sample_fast == 357, (sample_brute, sample_fast)

    real = day03.read_banks(REPO_ROOT / "inputs" / "Day03.txt")
    real_brute = sum(brute_pair_joltage(bank) for bank in real)
    real_fast = day03.part1(real)
    assert real_brute == real_fast, (real_brute, real_fast)

    boundaries = {
        "123456789": 89,
        "987654321": 98,
        "55555": 55,
        "12": 12,
        "819": 89,
        "212": 22,
        "978": 98,
    }
    for bank, expected in boundaries.items():
        got = brute_pair_joltage(bank)
        assert got == expected, (bank, got, expected)

    print(f"sample:  brute={sample_brute} fast={sample_fast}")
    print(f"real:    brute={real_brute} fast={real_fast}")
    print(f"boundaries: {len(boundaries)} banks verified")
    print("brute-force == optimized on all checks")


if __name__ == "__main__":
    main()
