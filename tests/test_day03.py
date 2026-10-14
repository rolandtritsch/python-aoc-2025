"""Day03 examples, digit-order boundaries, and input parsing."""

from pathlib import Path

import pytest

from aoc2025 import day03

INPUTS = Path(__file__).resolve().parents[1] / "inputs"

SAMPLE_BANKS = [
    "987654321111111",
    "811111111111119",
    "234234234234278",
    "818181911112111",
]


def test_part1_sample() -> None:
    assert day03.part1(SAMPLE_BANKS) == 357


def test_part1_bundled_sample_file() -> None:
    banks = day03.read_banks(INPUTS / "Day03Test.txt")
    assert banks == SAMPLE_BANKS
    assert day03.part1(banks) == 357


def test_part1_real_input() -> None:
    banks = day03.read_banks(INPUTS / "Day03.txt")
    assert day03.part1(banks) == 17207


def test_part1_no_banks() -> None:
    assert day03.part1([]) == 0


def test_part1_two_digit_bank() -> None:
    assert day03.part1(["12"]) == 12


def test_part1_ascending_bank() -> None:
    assert day03.part1(["123456789"]) == 89


def test_part1_descending_bank() -> None:
    assert day03.part1(["987654321"]) == 98


def test_part1_equal_digits() -> None:
    assert day03.part1(["55555"]) == 55


@pytest.mark.parametrize(
    ("bank", "expected"),
    [
        ("12", 12),
        ("123456789", 89),
        ("987654321", 98),
        ("819", 89),
        ("212", 22),
        ("978", 98),
        ("55555", 55),
    ],
)
def test_largest_pair_joltage(bank: str, expected: int) -> None:
    assert day03.largest_pair_joltage(bank) == expected


def test_largest_pair_joltage_too_short() -> None:
    with pytest.raises(ValueError, match="at least two"):
        day03.largest_pair_joltage("1")


def test_read_banks_empty_filename() -> None:
    with pytest.raises(ValueError, match="filename"):
        day03.read_banks("")


def test_read_banks_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        day03.read_banks(tmp_path / "missing.txt")


def test_read_banks_without_final_newline(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("987654321", encoding="utf-8")
    assert day03.read_banks(path) == ["987654321"]


@pytest.mark.parametrize(
    "content",
    [
        "\n",
        "12a4\n",
        "1\n",
        "12\n\n34\n",
    ],
)
def test_read_banks_invalid_lines(tmp_path: Path, content: str) -> None:
    path = tmp_path / "input.txt"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError):
        day03.read_banks(path)
