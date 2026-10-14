"""Day08 examples, circuit boundary cases, and input parsing."""

from pathlib import Path

import pytest

from aoc2025 import day08

INPUTS = Path(__file__).resolve().parents[1] / "inputs"

SAMPLE_BOXES = [
    day08.Box(162, 817, 812),
    day08.Box(57, 618, 57),
    day08.Box(906, 360, 560),
    day08.Box(592, 479, 940),
    day08.Box(352, 342, 300),
    day08.Box(466, 668, 158),
    day08.Box(542, 29, 236),
    day08.Box(431, 825, 988),
    day08.Box(739, 650, 466),
    day08.Box(52, 470, 668),
    day08.Box(216, 146, 977),
    day08.Box(819, 987, 18),
    day08.Box(117, 168, 530),
    day08.Box(805, 96, 715),
    day08.Box(346, 949, 466),
    day08.Box(970, 615, 88),
    day08.Box(941, 993, 340),
    day08.Box(862, 61, 35),
    day08.Box(984, 92, 344),
    day08.Box(425, 690, 689),
]


def test_part1_sample() -> None:
    assert day08.part1(SAMPLE_BOXES, connections=10) == 40


def test_part1_bundled_sample_file() -> None:
    boxes = day08.read_boxes(INPUTS / "Day08Test.txt")
    assert boxes == SAMPLE_BOXES
    assert day08.part1(boxes, connections=10) == 40


def test_part1_real_input() -> None:
    boxes = day08.read_boxes(INPUTS / "Day08.txt")
    assert day08.part1(boxes) == 90036


def test_part1_three_boxes_single_triangle() -> None:
    boxes = [day08.Box(0, 0, 0), day08.Box(0, 0, 1), day08.Box(0, 0, 2)]
    assert day08.part1(boxes, connections=2) == 3


def test_part1_four_boxes_two_pairs() -> None:
    boxes = [
        day08.Box(0, 0, 0),
        day08.Box(0, 0, 1),
        day08.Box(100, 100, 100),
        day08.Box(100, 100, 101),
    ]
    assert day08.part1(boxes, connections=2) == 2 * 2 * 1


def test_part1_five_boxes_two_pairs_and_singleton() -> None:
    boxes = [
        day08.Box(0, 0, 0),
        day08.Box(0, 0, 1),
        day08.Box(100, 100, 100),
        day08.Box(100, 100, 101),
        day08.Box(1000, 1000, 1000),
    ]
    assert day08.part1(boxes, connections=2) == 2 * 2 * 1


def test_part1_too_few_boxes_raises() -> None:
    with pytest.raises(ValueError, match="at least three"):
        day08.part1([day08.Box(0, 0, 0), day08.Box(1, 1, 1)])


def test_read_boxes_empty_filename() -> None:
    with pytest.raises(ValueError, match="filename"):
        day08.read_boxes("")


def test_read_boxes_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        day08.read_boxes(tmp_path / "missing.txt")


def test_read_boxes_blank_line(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("1,2,3\n\n4,5,6\n", encoding="utf-8")
    with pytest.raises(ValueError, match="blank"):
        day08.read_boxes(path)


def test_read_boxes_missing_comma(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("1,2 3\n", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid triple"):
        day08.read_boxes(path)


def test_read_boxes_non_integer(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("1,x,3\n", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid triple"):
        day08.read_boxes(path)


def test_read_boxes_negative_coordinates(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("-1,2,3\n", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid triple"):
        day08.read_boxes(path)


def test_read_boxes_without_final_newline(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("1,2,3\n4,5,6", encoding="utf-8")
    assert day08.read_boxes(path) == [day08.Box(1, 2, 3), day08.Box(4, 5, 6)]
