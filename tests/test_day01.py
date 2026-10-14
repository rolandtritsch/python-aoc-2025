"""Day01 examples, dial boundary behavior, and input parsing."""

from pathlib import Path

import pytest

from aoc2025 import day01
from aoc2025.day01 import Rotation

INPUTS = Path(__file__).resolve().parents[1] / "inputs"

SAMPLE_ROTATIONS = [
    Rotation("L", 68),
    Rotation("L", 30),
    Rotation("R", 48),
    Rotation("L", 5),
    Rotation("R", 60),
    Rotation("L", 55),
    Rotation("L", 1),
    Rotation("L", 99),
    Rotation("R", 14),
    Rotation("L", 82),
]


def test_part1_sample() -> None:
    assert day01.part1(SAMPLE_ROTATIONS) == 3


def test_part1_bundled_sample_file() -> None:
    rotations = day01.read_rotations(INPUTS / "Day01Test.txt")
    assert rotations == SAMPLE_ROTATIONS
    assert day01.part1(rotations) == 3


def test_part1_real_input() -> None:
    rotations = day01.read_rotations(INPUTS / "Day01.txt")
    assert day01.part1(rotations) == 1129


def test_part1_no_rotations() -> None:
    assert day01.part1([]) == 0


def test_part1_right_rotation_lands_on_zero() -> None:
    assert day01.part1([Rotation("R", 50)]) == 1


def test_part1_left_rotation_skips_zero() -> None:
    assert day01.part1([Rotation("L", 1)]) == 0


def test_part1_full_circle_returns_to_start() -> None:
    assert day01.part1([Rotation("R", 100)]) == 0


@pytest.mark.parametrize(
    ("rotation", "start", "expected"),
    [
        (Rotation("R", 8), 11, 19),
        (Rotation("L", 19), 19, 0),
        (Rotation("L", 1), 0, 99),
        (Rotation("R", 1), 99, 0),
        (Rotation("L", 10), 5, 95),
        (Rotation("R", 5), 95, 0),
    ],
)
def test_apply_rotation(rotation: Rotation, start: int, expected: int) -> None:
    assert day01.apply_rotation(rotation, start) == expected


def test_apply_rotation_invalid_direction() -> None:
    with pytest.raises(ValueError, match="direction"):
        day01.apply_rotation(Rotation("X", 1), 0)


def test_read_rotations_empty_filename() -> None:
    with pytest.raises(ValueError, match="filename"):
        day01.read_rotations("")


def test_read_rotations_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        day01.read_rotations(tmp_path / "missing.txt")


@pytest.mark.parametrize(
    "content",
    [
        "X10\n",
        "L\n",
        "L10x\n",
        "L10\n\n",
        "L10\nR\n",
    ],
)
def test_read_rotations_invalid_lines(tmp_path: Path, content: str) -> None:
    path = tmp_path / "input.txt"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(ValueError):
        day01.read_rotations(path)


def test_read_rotations_without_final_newline(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("L5\nR3", encoding="utf-8")
    assert day01.read_rotations(path) == [Rotation("L", 5), Rotation("R", 3)]
