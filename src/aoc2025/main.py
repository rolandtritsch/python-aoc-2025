"""Run the implemented daily solutions from an editable repository checkout."""

from pathlib import Path

from aoc2025 import day00, day01, day02, day03


def solve() -> None:
    """Read checkout-local inputs and print every implemented part's answer.

    The top-level inputs directory belongs to the checkout, not the installed
    package. Use uv sync's default editable installation to run this command.
    """
    inputs = Path(__file__).resolve().parents[2] / "inputs"
    values = day00.read_file(inputs / "Day00.txt")
    print(f"Day00 - part1: {day00.part1(values)}")
    print(f"Day00 - part2: {day00.part2(values)}")
    rotations = day01.read_rotations(inputs / "Day01.txt")
    print(f"Day01 - part1: {day01.part1(rotations)}")
    print(f"Day01 - part2: {day01.part2(rotations)}")
    ranges = day02.read_ranges(inputs / "Day02.txt")
    print(f"Day02 - part1: {day02.part1(ranges)}")
    print(f"Day02 - part2: {day02.part2(ranges)}")
    banks = day03.read_banks(inputs / "Day03.txt")
    print(f"Day03 - part1: {day03.part1(banks)}")
    print(f"Day03 - part2: {day03.part2(banks)}")
