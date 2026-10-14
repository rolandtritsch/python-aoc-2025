"""Day02 examples, digit-pattern boundaries, and input parsing."""

from pathlib import Path

import pytest

from aoc2025 import day02
from aoc2025.day02 import IdRange

INPUTS = Path(__file__).resolve().parents[1] / "inputs"

SAMPLE_RANGES = [
    IdRange(11, 22),
    IdRange(95, 115),
    IdRange(998, 1012),
    IdRange(1188511880, 1188511890),
    IdRange(222220, 222224),
    IdRange(1698522, 1698528),
    IdRange(446443, 446449),
    IdRange(38593856, 38593862),
    IdRange(565653, 565659),
    IdRange(824824821, 824824827),
    IdRange(2121212118, 2121212124),
]


def test_part1_sample() -> None:
    assert day02.part1(SAMPLE_RANGES) == 1227775554


def test_part1_bundled_sample_file() -> None:
    ranges = day02.read_ranges(INPUTS / "Day02Test.txt")
    assert ranges == SAMPLE_RANGES
    assert day02.part1(ranges) == 1227775554


def test_part1_real_input() -> None:
    ranges = day02.read_ranges(INPUTS / "Day02.txt")
    assert day02.part1(ranges) == 44487518055


def test_part1_no_ranges() -> None:
    assert day02.part1([]) == 0


def test_part1_range_without_invalid_ids() -> None:
    assert day02.part1([IdRange(10, 10)]) == 0
    assert day02.part1([IdRange(123, 129)]) == 0


def test_part1_single_doubled_id() -> None:
    assert day02.part1([IdRange(11, 11)]) == 11


@pytest.mark.parametrize(
    ("number", "expected"),
    [
        (11, True),
        (22, True),
        (99, True),
        (1010, True),
        (6464, True),
        (123123, True),
        (1188511885, True),
        (0, False),
        (5, False),
        (10, False),
        (12, False),
        (101, False),
        (111, False),
        (998, False),
        (1001, False),
    ],
)
def test_is_repeated_twice(number: int, expected: bool) -> None:
    assert day02.is_repeated_twice(number) is expected


def test_is_repeated_twice_negative() -> None:
    with pytest.raises(ValueError, match="nonnegative"):
        day02.is_repeated_twice(-1)


def test_read_ranges_empty_filename() -> None:
    with pytest.raises(ValueError, match="filename"):
        day02.read_ranges("")


def test_read_ranges_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        day02.read_ranges(tmp_path / "missing.txt")


def test_read_ranges_without_final_newline(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("11-22,95-115", encoding="utf-8")
    assert day02.read_ranges(path) == [IdRange(11, 22), IdRange(95, 115)]


def test_read_ranges_skips_blank_lines(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("11-22\n\n95-115\n", encoding="utf-8")
    assert day02.read_ranges(path) == [IdRange(11, 22), IdRange(95, 115)]


@pytest.mark.parametrize(
    "content",
    [
        "11\n",
        "11-22-33\n",
        "11-,\n",
        "-22\n",
        "a-b\n",
        "22-11\n",
        "11,,22\n",
    ],
)
def test_read_ranges_invalid_tokens(tmp_path: Path, content: str) -> None:
    path = tmp_path / "input.txt"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError):
        day02.read_ranges(path)
