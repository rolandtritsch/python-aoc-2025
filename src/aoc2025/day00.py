"""Day00: compute Fibonacci numbers from the first and last input integers.

This is a runnable template, not an official Advent of Code puzzle.
The bundled input selects fib(10) for part 1 and fib(1000) for part 2.
Python integers preserve the complete 209-digit result of part 2.
"""

from collections.abc import Sequence
from pathlib import Path


def fib(n: int) -> int:
    """Return Fibonacci number n, with fib(0) = 0 and fib(1) = 1.

    Raise ValueError for negative indices. Iteration avoids recursion limits.
    """
    if n < 0:
        raise ValueError("n must be nonnegative")
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def read_file(filename: str | Path) -> list[int]:
    """Read one integer per line from a UTF-8 input file.

    Whitespace around integers is allowed. Malformed or blank lines raise
    ValueError; missing files raise FileNotFoundError.
    """
    if not str(filename):
        raise ValueError("filename must not be empty")
    with Path(filename).open(encoding="utf-8") as source:
        return [int(line.strip()) for line in source]


def part1(values: Sequence[int]) -> int:
    """Return fib of the first input integer; reject an empty sequence."""
    if not values:
        raise ValueError("input must not be empty")
    return fib(values[0])


def part2(values: Sequence[int]) -> int:
    """Return fib of the last input integer; reject an empty sequence."""
    if not values:
        raise ValueError("input must not be empty")
    return fib(values[-1])
