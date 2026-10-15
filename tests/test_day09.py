"""Day09 example, rectangle boundary cases, and input parsing."""

from pathlib import Path

import pytest

from aoc2025 import day09

INPUTS = Path(__file__).resolve().parents[1] / "inputs"

SAMPLE_TILES = [
    day09.Tile(7, 1),
    day09.Tile(11, 1),
    day09.Tile(11, 7),
    day09.Tile(9, 7),
    day09.Tile(9, 5),
    day09.Tile(2, 5),
    day09.Tile(2, 3),
    day09.Tile(7, 3),
]


def test_part1_sample() -> None:
    assert day09.part1(SAMPLE_TILES) == 50


def test_part1_bundled_sample_file() -> None:
    tiles = day09.read_tiles(INPUTS / "Day09Test.txt")
    assert tiles == SAMPLE_TILES
    assert day09.part1(tiles) == 50


def test_part1_real_input() -> None:
    tiles = day09.read_tiles(INPUTS / "Day09.txt")
    assert day09.part1(tiles) == 4777967538


def test_part1_two_tiles_rectangular() -> None:
    tiles = [day09.Tile(2, 5), day09.Tile(11, 1)]
    assert day09.part1(tiles) == 50


def test_part1_two_tiles_same_column() -> None:
    tiles = [day09.Tile(7, 1), day09.Tile(7, 3)]
    assert day09.part1(tiles) == 3


def test_part1_two_tiles_same_row() -> None:
    tiles = [day09.Tile(2, 3), day09.Tile(7, 3)]
    assert day09.part1(tiles) == 6


def test_part1_identical_tiles() -> None:
    tiles = [day09.Tile(4, 4), day09.Tile(4, 4)]
    assert day09.part1(tiles) == 1


def test_part1_three_tiles_picks_widest_pair() -> None:
    tiles = [day09.Tile(0, 0), day09.Tile(0, 1), day09.Tile(9, 0)]
    assert day09.part1(tiles) == 20


def test_part2_sample() -> None:
    assert day09.part2(SAMPLE_TILES) == 24


def test_part2_bundled_sample_file() -> None:
    tiles = day09.read_tiles(INPUTS / "Day09Test.txt")
    assert day09.part2(tiles) == 24


def test_part2_real_input() -> None:
    tiles = day09.read_tiles(INPUTS / "Day09.txt")
    assert day09.part2(tiles) == 1439894345


def test_part2_tiny_square_loop() -> None:
    tiles = [
        day09.Tile(0, 0),
        day09.Tile(2, 0),
        day09.Tile(2, 2),
        day09.Tile(0, 2),
    ]
    assert day09.part2(tiles) == 9


def test_part2_thin_rectangle_loop() -> None:
    tiles = [
        day09.Tile(0, 0),
        day09.Tile(4, 0),
        day09.Tile(4, 1),
        day09.Tile(0, 1),
    ]
    assert day09.part2(tiles) == 10


def test_part2_interior_prunes_diagonal_corner() -> None:
    tiles = [
        day09.Tile(0, 0),
        day09.Tile(3, 0),
        day09.Tile(3, 1),
        day09.Tile(1, 1),
        day09.Tile(1, 3),
        day09.Tile(0, 3),
    ]
    assert day09.part2(tiles) == 8


def test_part2_single_tile_raises() -> None:
    with pytest.raises(ValueError, match="at least two"):
        day09.part2([day09.Tile(0, 0)])


def test_part1_single_tile_raises() -> None:
    with pytest.raises(ValueError, match="at least two"):
        day09.part1([day09.Tile(0, 0)])


def test_read_tiles_empty_filename() -> None:
    with pytest.raises(ValueError, match="filename"):
        day09.read_tiles("")


def test_read_tiles_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        day09.read_tiles(tmp_path / "missing.txt")


def test_read_tiles_blank_line(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("1,2\n\n3,4\n", encoding="utf-8")
    with pytest.raises(ValueError, match="blank"):
        day09.read_tiles(path)


def test_read_tiles_missing_comma(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("1 2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid coordinate"):
        day09.read_tiles(path)


def test_read_tiles_three_parts(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("1,2,3\n", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid coordinate"):
        day09.read_tiles(path)


def test_read_tiles_non_integer(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("1,x\n", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid coordinate"):
        day09.read_tiles(path)


def test_read_tiles_negative_coordinates(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("-1,2\n", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid coordinate"):
        day09.read_tiles(path)


def test_read_tiles_without_final_newline(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("1,2\n3,4", encoding="utf-8")
    assert day09.read_tiles(path) == [day09.Tile(1, 2), day09.Tile(3, 4)]
