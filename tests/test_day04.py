"""Day04 examples, adjacency boundaries, and input parsing."""

from pathlib import Path

import pytest

from aoc2025 import day04

INPUTS = Path(__file__).resolve().parents[1] / "inputs"

SAMPLE_GRID = [
    "..@@.@@@@.",
    "@@@.@.@.@@",
    "@@@@@.@.@@",
    "@.@@@@..@.",
    "@@.@@@@.@@",
    ".@@@@@@@.@",
    ".@.@.@.@@@",
    "@.@@@.@@@@",
    ".@@@@@@@@.",
    "@.@.@@@.@.",
]


def test_part1_sample() -> None:
    assert day04.part1(SAMPLE_GRID) == 13


def test_part1_bundled_sample_file() -> None:
    grid = day04.read_grid(INPUTS / "Day04Test.txt")
    assert grid == SAMPLE_GRID
    assert day04.part1(grid) == 13


def test_part1_real_input() -> None:
    grid = day04.read_grid(INPUTS / "Day04.txt")
    assert day04.part1(grid) == 1356


def test_part1_empty_grid() -> None:
    assert day04.part1([]) == 0


def test_part1_single_isolated_roll() -> None:
    assert day04.part1(["@"]) == 1


def test_part1_full_block_corners_only() -> None:
    # Interior and edge rolls have at least four neighbours; only the four
    # corners (three neighbours each) stay accessible.
    assert day04.part1(["@@@", "@@@", "@@@"]) == 4
    assert day04.part1(["@@@@", "@@@@", "@@@@", "@@@@"]) == 4


def test_part1_exactly_four_neighbours_not_accessible() -> None:
    # The left-middle roll has exactly four neighbours and is excluded, while
    # the top and bottom rolls with fewer neighbours remain accessible.
    assert day04.part1([".@.", "@@.", "@@."]) == 3


def test_part1_diagonal_neighbours_counted() -> None:
    # Each roll here has two diagonal neighbours and stays accessible.
    assert day04.part1([".@.", "@.@", ".@."]) == 4


def test_read_grid_invalid_character(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text(".x.\n", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid"):
        day04.read_grid(path)


def test_read_grid_ragged_lines(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("..\n...\n", encoding="utf-8")
    with pytest.raises(ValueError, match="length"):
        day04.read_grid(path)


def test_read_grid_blank_line(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text(".@.\n\n...\n", encoding="utf-8")
    with pytest.raises(ValueError, match="blank"):
        day04.read_grid(path)


def test_read_grid_empty_filename() -> None:
    with pytest.raises(ValueError, match="filename"):
        day04.read_grid("")


def test_read_grid_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        day04.read_grid(tmp_path / "missing.txt")


def test_read_grid_without_final_newline(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text(".@.", encoding="utf-8")
    assert day04.read_grid(path) == [".@."]
