"""Run the implemented daily solutions from an editable repository checkout."""

from pathlib import Path

from aoc2025 import day00


def solve() -> None:
    """Read checkout-local inputs and print the answers for both Day00 parts.

    The top-level inputs directory belongs to the checkout, not the installed
    package. Use uv sync's default editable installation to run this command.
    """
    inputs = Path(__file__).resolve().parents[2] / "inputs"
    values = day00.read_file(inputs / "Day00.txt")
    print(f"Day00 - part1: {day00.part1(values)}")
    print(f"Day00 - part2: {day00.part2(values)}")
