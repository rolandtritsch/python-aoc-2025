"""Run the implemented daily solutions from an editable repository checkout."""

from pathlib import Path

from aoc2025 import day00, day01, day02, day03, day04, day05, day06, day07, day08, day09


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
    rolls = day04.read_grid(inputs / "Day04.txt")
    print(f"Day04 - part1: {day04.part1(rolls)}")
    print(f"Day04 - part2: {day04.part2(rolls)}")
    database = day05.read_database(inputs / "Day05.txt")
    print(f"Day05 - part1: {day05.part1(database.ranges, database.available)}")
    print(f"Day05 - part2: {day05.part2(database.ranges)}")
    worksheet = day06.read_worksheet(inputs / "Day06.txt")
    print(f"Day06 - part1: {day06.part1(worksheet)}")
    grid = day06.read_grid(inputs / "Day06.txt")
    print(f"Day06 - part2: {day06.part2(grid)}")
    manifold = day07.read_grid(inputs / "Day07.txt")
    print(f"Day07 - part1: {day07.part1(manifold)}")
    print(f"Day07 - part2: {day07.part2(manifold)}")
    boxes = day08.read_boxes(inputs / "Day08.txt")
    print(f"Day08 - part1: {day08.part1(boxes)}")
    print(f"Day08 - part2: {day08.part2(boxes)}")
    tiles = day09.read_tiles(inputs / "Day09.txt")
    print(f"Day09 - part1: {day09.part1(tiles)}")
