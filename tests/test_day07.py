"""Day07 examples, splitting boundaries, and input parsing."""

from pathlib import Path

import pytest

from aoc2025 import day07

INPUTS = Path(__file__).resolve().parents[1] / "inputs"

SAMPLE_GRID = [
    ".......S.......",
    "...............",
    ".......^.......",
    "...............",
    "......^.^......",
    "...............",
    ".....^.^.^.....",
    "...............",
    "....^.^...^....",
    "...............",
    "...^.^...^.^...",
    "...............",
    "..^...^.....^..",
    "...............",
    ".^.^.^.^.^...^.",
    "...............",
]


def test_part1_sample() -> None:
    assert day07.part1(SAMPLE_GRID) == 21


def test_part1_bundled_sample_file() -> None:
    grid = day07.read_grid(INPUTS / "Day07Test.txt")
    assert grid == SAMPLE_GRID
    assert day07.part1(grid) == 21


def test_part1_real_input() -> None:
    grid = day07.read_grid(INPUTS / "Day07.txt")
    assert day07.part1(grid) == 1605


def test_part1_empty_grid() -> None:
    assert day07.part1([]) == 0


def test_part1_missing_start_raises() -> None:
    with pytest.raises(ValueError, match="exactly one S"):
        day07.part1(["..", ".."])


def test_part1_single_cell() -> None:
    assert day07.part1(["S"]) == 0


def test_part1_no_splitter_straight_down() -> None:
    assert day07.part1(["S", ".", ".", "."]) == 0


def test_part1_single_splitter() -> None:
    assert day07.part1(["S", ".", "^"]) == 1


def test_part1_splitter_off_path_is_missed() -> None:
    assert day07.part1(["S.", ".^"]) == 0


def test_part1_merged_beams_split_once() -> None:
    grid = [
        ".S.",
        ".^.",
        "...",
        "^.^",
        "...",
        ".^.",
        "...",
    ]
    assert day07.part1(grid) == 4


def test_part1_splitter_at_left_edge_drops_negative() -> None:
    assert day07.part1(["S..", "^..", "..."]) == 1


def test_part1_splitter_at_right_edge_drops_out_of_range() -> None:
    assert day07.part1(["..S", "..^"]) == 1


def test_part1_adjacent_splitters_spawn_down_not_sideways() -> None:
    grid = [
        ".S..",
        ".^^.",
        "....",
        ".^.^",
    ]
    assert day07.part1(grid) == 1


def test_read_grid_empty_filename() -> None:
    with pytest.raises(ValueError, match="filename"):
        day07.read_grid("")


def test_read_grid_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        day07.read_grid(tmp_path / "missing.txt")


def test_read_grid_empty_content(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="empty"):
        day07.read_grid(path)


def test_read_grid_blank_line(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("S\n\n..\n", encoding="utf-8")
    with pytest.raises(ValueError, match="blank"):
        day07.read_grid(path)


def test_read_grid_ragged_lines(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("S\n..\n", encoding="utf-8")
    with pytest.raises(ValueError, match="same length"):
        day07.read_grid(path)


def test_read_grid_invalid_character(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("S.\n.x\n", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid character"):
        day07.read_grid(path)


def test_read_grid_missing_start(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("..\n..\n", encoding="utf-8")
    with pytest.raises(ValueError, match="exactly one S"):
        day07.read_grid(path)


def test_read_grid_duplicate_start(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("S.\n.S\n", encoding="utf-8")
    with pytest.raises(ValueError, match="exactly one S"):
        day07.read_grid(path)


def test_read_grid_without_final_newline(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text(".S.\n.^.\n...", encoding="utf-8")
    assert day07.read_grid(path) == [".S.", ".^.", "..."]
